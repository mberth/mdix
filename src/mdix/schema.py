from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import yaml

from .vault import iter_markdown_files, path_in_scope


@dataclass(frozen=True)
class SchemaField:
    name: str
    required: bool
    expected_type: str
    enum: tuple[Any, ...] | None


@dataclass(frozen=True)
class MigrationOperation:
    op: str
    source: str | None = None
    target: str | None = None
    field: str | None = None
    value: Any = None
    mapping: tuple[tuple[Any, Any], ...] = ()


@dataclass(frozen=True)
class SchemaContract:
    path: Path
    fields: tuple[SchemaField, ...]
    migrations: tuple[MigrationOperation, ...]


@dataclass(frozen=True)
class ParsedNote:
    has_frontmatter: bool
    frontmatter: dict[str, Any] | None
    body: str
    errors: list[dict[str, str]]


TYPE_CHECKERS: dict[str, type[Any] | tuple[type[Any], ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _is_json_scalar_like(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _normalize_scalar_for_json(value: Any) -> Any:
    if _is_json_scalar_like(value):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def to_json_compatible(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): to_json_compatible(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_json_compatible(item) for item in value]
    if isinstance(value, tuple):
        return [to_json_compatible(item) for item in value]
    return _normalize_scalar_for_json(value)


def _has_frontmatter_block(text: str) -> bool:
    return text.startswith("---\n") or text.startswith("---\r\n")


def _read_note(path: Path) -> ParsedNote:
    text = path.read_text(encoding="utf-8")
    if not _has_frontmatter_block(text):
        return ParsedNote(has_frontmatter=False, frontmatter=None, body=text, errors=[])

    lines = text.splitlines(keepends=True)
    closing_index: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = i
            break

    if closing_index is None:
        return ParsedNote(
            has_frontmatter=True,
            frontmatter=None,
            body=text,
            errors=[{"type": "yaml_error", "message": "Frontmatter block is missing closing '---' delimiter."}],
        )

    yaml_text = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])
    try:
        loaded = yaml.safe_load(yaml_text) if yaml_text.strip() else {}
    except yaml.YAMLError as e:
        return ParsedNote(
            has_frontmatter=True,
            frontmatter=None,
            body=body,
            errors=[{"type": "yaml_error", "message": str(e)}],
        )

    if loaded is None:
        loaded = {}

    if not isinstance(loaded, dict):
        return ParsedNote(
            has_frontmatter=True,
            frontmatter=None,
            body=body,
            errors=[{"type": "frontmatter_error", "message": "Frontmatter must parse to a mapping/object."}],
        )

    return ParsedNote(has_frontmatter=True, frontmatter=loaded, body=body, errors=[])


def _format_frontmatter(frontmatter_obj: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(frontmatter_obj, sort_keys=True, allow_unicode=True).rstrip()
    return f"---\n{dumped}\n---\n"


def write_note(path: Path, frontmatter_obj: dict[str, Any], body: str) -> None:
    path.write_text(_format_frontmatter(frontmatter_obj) + body, encoding="utf-8")


def _get_at_path(data: dict[str, Any] | None, dotted: str) -> tuple[bool, Any]:
    if data is None:
        return (False, None)
    current: Any = data
    for segment in dotted.split("."):
        if not isinstance(current, dict) or segment not in current:
            return (False, None)
        current = current[segment]
    return (True, current)


def _set_at_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    current: dict[str, Any] = data
    segments = dotted.split(".")
    for segment in segments[:-1]:
        existing = current.get(segment)
        if not isinstance(existing, dict):
            existing = {}
            current[segment] = existing
        current = existing
    current[segments[-1]] = value


def _delete_at_path(data: dict[str, Any], dotted: str) -> bool:
    current: dict[str, Any] = data
    segments = dotted.split(".")
    for segment in segments[:-1]:
        next_value = current.get(segment)
        if not isinstance(next_value, dict):
            return False
        current = next_value
    last = segments[-1]
    if last not in current:
        return False
    del current[last]
    return True


def _collect_null_paths(data: dict[str, Any], prefix: str = "") -> list[str]:
    found: list[str] = []
    for key in sorted(data.keys()):
        dotted = f"{prefix}.{key}" if prefix else key
        value = data[key]
        if value is None:
            found.append(dotted)
            continue
        if isinstance(value, dict):
            found.extend(_collect_null_paths(value, dotted))
    return found


def _title_from_relpath(rel_path: str) -> str:
    stem = PurePosixPath(rel_path).stem
    normalized = stem.replace("-", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in normalized.split())


def _apply_operations(
    frontmatter_obj: dict[str, Any],
    operations: tuple[MigrationOperation, ...],
    *,
    rel_path: str,
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for operation in operations:
        if operation.op == "rename":
            if operation.source is None or operation.target is None:
                continue
            source_exists, source_value = _get_at_path(frontmatter_obj, operation.source)
            if not source_exists:
                continue
            target_exists, _ = _get_at_path(frontmatter_obj, operation.target)
            if target_exists:
                continue
            if not _delete_at_path(frontmatter_obj, operation.source):
                continue
            _set_at_path(frontmatter_obj, operation.target, source_value)
            changes.append(
                {
                    "op": "rename",
                    "from": operation.source,
                    "to": operation.target,
                    "value": to_json_compatible(source_value),
                }
            )
            continue

        if operation.op == "value_map":
            if operation.field is None:
                continue
            exists, current_value = _get_at_path(frontmatter_obj, operation.field)
            if not exists:
                continue
            mapped_value: Any | None = None
            matched = False
            for source_value, target_value in operation.mapping:
                if current_value == source_value:
                    mapped_value = target_value
                    matched = True
                    break
            if not matched or mapped_value == current_value:
                continue
            _set_at_path(frontmatter_obj, operation.field, mapped_value)
            changes.append(
                {
                    "op": "value_map",
                    "field": operation.field,
                    "from": to_json_compatible(current_value),
                    "to": to_json_compatible(mapped_value),
                }
            )
            continue

        if operation.op == "set_default":
            if operation.field is None:
                continue
            exists, current_value = _get_at_path(frontmatter_obj, operation.field)
            if exists and current_value is not None:
                continue
            _set_at_path(frontmatter_obj, operation.field, operation.value)
            changes.append(
                {
                    "op": "set_default",
                    "field": operation.field,
                    "value": to_json_compatible(operation.value),
                }
            )
            continue

        if operation.op == "unset_if_null":
            if operation.field is None:
                continue
            exists, current_value = _get_at_path(frontmatter_obj, operation.field)
            if not exists or current_value is not None:
                continue
            if not _delete_at_path(frontmatter_obj, operation.field):
                continue
            changes.append({"op": "unset_if_null", "field": operation.field})
            continue

        if operation.op == "derive":
            if operation.field is None or operation.source is None:
                continue
            target_exists, target_value = _get_at_path(frontmatter_obj, operation.field)
            if target_exists and target_value is not None:
                continue
            source_exists, source_value = _get_at_path(frontmatter_obj, operation.source)
            if not source_exists or source_value is None:
                continue
            _set_at_path(frontmatter_obj, operation.field, source_value)
            changes.append(
                {
                    "op": "derive",
                    "field": operation.field,
                    "from": operation.source,
                    "value": to_json_compatible(source_value),
                    "source": "field",
                }
            )
            continue

        if operation.op == "derive_from_filename":
            if operation.field is None:
                continue
            target_exists, target_value = _get_at_path(frontmatter_obj, operation.field)
            if target_exists and target_value is not None:
                continue
            derived = _title_from_relpath(rel_path)
            _set_at_path(frontmatter_obj, operation.field, derived)
            changes.append(
                {
                    "op": "derive_from_filename",
                    "field": operation.field,
                    "value": derived,
                }
            )
            continue

        if operation.op == "remove_null_keys":
            null_paths = _collect_null_paths(frontmatter_obj)
            if not null_paths:
                continue
            removed_paths: list[str] = []
            for dotted in null_paths:
                if _delete_at_path(frontmatter_obj, dotted):
                    removed_paths.append(dotted)
            if removed_paths:
                changes.append(
                    {
                        "op": "remove_null_keys",
                        "fields": removed_paths,
                    }
                )
            continue

    return changes


def load_contract(schema_path: Path) -> SchemaContract:
    raw = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Schema contract must be a YAML object.")

    raw_fields = raw.get("fields")
    if not isinstance(raw_fields, dict):
        raise ValueError("Schema contract must define `fields` as a mapping.")

    fields: list[SchemaField] = []
    for field_name in sorted(raw_fields.keys()):
        spec = raw_fields[field_name]
        if not isinstance(spec, dict):
            raise ValueError(f"Field `{field_name}` must be an object.")
        expected_type = str(spec.get("type", "string"))
        if expected_type not in TYPE_CHECKERS:
            allowed = ", ".join(sorted(TYPE_CHECKERS.keys()))
            raise ValueError(f"Field `{field_name}` has unsupported type `{expected_type}` (allowed: {allowed}).")
        enum = spec.get("enum")
        if enum is not None and not isinstance(enum, list):
            raise ValueError(f"Field `{field_name}` enum must be a list.")
        fields.append(
            SchemaField(
                name=field_name,
                required=bool(spec.get("required", False)),
                expected_type=expected_type,
                enum=tuple(enum) if isinstance(enum, list) else None,
            )
        )

    migrations_parsed: list[MigrationOperation] = []
    migrations = raw.get("migrations", [])
    if migrations is None:
        migrations = []
    if not isinstance(migrations, list):
        raise ValueError("`migrations` must be a list when provided.")
    for migration in migrations:
        if not isinstance(migration, dict):
            raise ValueError("Each migration entry must be an object.")
        op = migration.get("op")
        if op == "rename":
            source = migration.get("from")
            target = migration.get("to")
            if not isinstance(source, str) or not source:
                raise ValueError("Rename migration requires non-empty string `from`.")
            if not isinstance(target, str) or not target:
                raise ValueError("Rename migration requires non-empty string `to`.")
            migrations_parsed.append(MigrationOperation(op="rename", source=source, target=target))
            continue

        if op == "value_map":
            field = migration.get("field")
            mapping = migration.get("map")
            if not isinstance(field, str) or not field:
                raise ValueError("Value-map migration requires non-empty string `field`.")
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError("Value-map migration requires non-empty object `map`.")
            migrations_parsed.append(MigrationOperation(op="value_map", field=field, mapping=tuple(mapping.items())))
            continue

        if op == "set_default":
            field = migration.get("field")
            if not isinstance(field, str) or not field:
                raise ValueError("Set-default migration requires non-empty string `field`.")
            if "value" not in migration:
                raise ValueError("Set-default migration requires `value`.")
            migrations_parsed.append(MigrationOperation(op="set_default", field=field, value=migration["value"]))
            continue

        if op == "unset_if_null":
            field = migration.get("field")
            if not isinstance(field, str) or not field:
                raise ValueError("Unset-if-null migration requires non-empty string `field`.")
            migrations_parsed.append(MigrationOperation(op="unset_if_null", field=field))
            continue

        allowed = "rename, value_map, set_default, unset_if_null"
        raise ValueError(f"Unsupported migration op `{op}` (allowed: {allowed}).")

    return SchemaContract(path=schema_path, fields=tuple(fields), migrations=tuple(migrations_parsed))


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _schema_source_path(root: Path, schema_path: Path) -> str:
    resolved_schema = schema_path.resolve()
    try:
        return resolved_schema.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved_schema.as_posix()





def validate_vault(
    root: Path,
    contract: SchemaContract,
    *,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    files_scanned = 0
    files_with_frontmatter = 0
    files_validated = 0
    files_with_violations: set[str] = set()
    parse_errors = 0

    for note_path in iter_markdown_files(root):
        rel = note_path.resolve().relative_to(root.resolve()).as_posix()
        if not path_in_scope(rel, include, exclude):
            continue
        files_scanned += 1
        note = _read_note(note_path)
        if note.has_frontmatter:
            files_with_frontmatter += 1
        if note.errors:
            parse_errors += 1
            files_with_violations.add(rel)
            violations.append(
                {
                    "code": "FRONTMATTER_PARSE_ERROR",
                    "path": rel,
                    "field": None,
                    "message": note.errors[0]["message"],
                    "actual": note.errors[0]["type"],
                    "expected": "valid frontmatter mapping",
                }
            )
            continue

        if note.frontmatter is None:
            # Files without a frontmatter block are outside schema validation scope.
            continue

        files_validated += 1
        frontmatter_obj = note.frontmatter
        for field in contract.fields:
            exists, value = _get_at_path(frontmatter_obj, field.name)
            if field.required and not exists:
                files_with_violations.add(rel)
                violations.append(
                    {
                        "code": "SCHEMA_REQUIRED_MISSING",
                        "path": rel,
                        "field": field.name,
                        "message": f"Missing required field `{field.name}`.",
                        "actual": None,
                        "expected": {"required": True},
                    }
                )
                continue
            if not exists:
                continue

            checker = TYPE_CHECKERS[field.expected_type]
            if not isinstance(value, checker):
                files_with_violations.add(rel)
                violations.append(
                    {
                        "code": "SCHEMA_TYPE_MISMATCH",
                        "path": rel,
                        "field": field.name,
                        "message": f"Field `{field.name}` has wrong type.",
                        "actual": _type_name(value),
                        "expected": field.expected_type,
                    }
                )
                continue

            if field.enum is not None and value not in field.enum:
                files_with_violations.add(rel)
                violations.append(
                    {
                        "code": "SCHEMA_ENUM_MISMATCH",
                        "path": rel,
                        "field": field.name,
                        "message": f"Field `{field.name}` value is outside allowed enum.",
                        "actual": value,
                        "expected": list(field.enum),
                    }
                )

    violations.sort(key=lambda item: (item["path"], item["code"], str(item["field"])))
    summary = {
        "files_scanned": files_scanned,
        "files_with_frontmatter": files_with_frontmatter,
        "files_validated": files_validated,
        "files_with_violations": len(files_with_violations),
        "files_valid": files_validated - len(files_with_violations),
        "parse_errors": parse_errors,
        "violations": len(violations),
    }
    return {
        "schema": _schema_source_path(root, contract.path),
        "summary": summary,
        "violations": violations,
    }


def migrate_vault(
    root: Path,
    contract: SchemaContract,
    *,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    dry_run: bool,
) -> dict[str, Any]:
    files_scanned = 0
    files_changed = 0
    parse_errors = 0
    skipped_no_frontmatter = 0
    total_operations = 0
    changes: list[dict[str, Any]] = []

    for note_path in iter_markdown_files(root):
        rel = note_path.resolve().relative_to(root.resolve()).as_posix()
        if not path_in_scope(rel, include, exclude):
            continue
        files_scanned += 1
        note = _read_note(note_path)
        if note.errors:
            parse_errors += 1
            changes.append(
                {
                    "path": rel,
                    "status": "parse_error",
                    "errors": note.errors,
                    "changes": [],
                }
            )
            continue

        if note.frontmatter is None:
            skipped_no_frontmatter += 1
            continue

        updated = dict(note.frontmatter)
        file_changes = _apply_operations(updated, contract.migrations, rel_path=rel)

        if file_changes:
            files_changed += 1
            total_operations += len(file_changes)
            if not dry_run:
                write_note(note_path, updated, note.body)
            changes.append({"path": rel, "status": "updated" if not dry_run else "preview", "changes": file_changes})

    changes.sort(key=lambda item: item["path"])
    return {
        "schema": _schema_source_path(root, contract.path),
        "summary": {
            "files_scanned": files_scanned,
            "files_changed": files_changed,
            "operations": total_operations,
            "parse_errors": parse_errors,
            "skipped_no_frontmatter": skipped_no_frontmatter,
            "dry_run": dry_run,
        },
        "changes": changes,
    }


def normalize_vault(
    root: Path,
    *,
    operations: tuple[MigrationOperation, ...],
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    dry_run: bool,
) -> dict[str, Any]:
    files_scanned = 0
    files_changed = 0
    parse_errors = 0
    skipped_no_frontmatter = 0
    total_operations = 0
    changes: list[dict[str, Any]] = []

    for note_path in iter_markdown_files(root):
        rel = note_path.resolve().relative_to(root.resolve()).as_posix()
        if not path_in_scope(rel, include, exclude):
            continue
        files_scanned += 1
        note = _read_note(note_path)
        if note.errors:
            parse_errors += 1
            changes.append(
                {
                    "path": rel,
                    "status": "parse_error",
                    "errors": note.errors,
                    "changes": [],
                }
            )
            continue

        if note.frontmatter is None:
            skipped_no_frontmatter += 1
            continue

        updated = dict(note.frontmatter)
        file_changes = _apply_operations(updated, operations, rel_path=rel)
        if not file_changes:
            continue

        files_changed += 1
        total_operations += len(file_changes)
        if not dry_run:
            write_note(note_path, updated, note.body)
        changes.append({"path": rel, "status": "updated" if not dry_run else "preview", "changes": file_changes})

    changes.sort(key=lambda item: item["path"])
    return {
        "summary": {
            "files_scanned": files_scanned,
            "files_changed": files_changed,
            "operations": total_operations,
            "parse_errors": parse_errors,
            "skipped_no_frontmatter": skipped_no_frontmatter,
            "dry_run": dry_run,
        },
        "changes": changes,
    }


def inventory_vault(root: Path) -> dict[str, Any]:
    files_scanned = 0
    files_with_frontmatter = 0
    parse_errors = 0
    key_counts: dict[str, int] = {}

    def collect(obj: dict[str, Any], prefix: str = "") -> None:
        for key in sorted(obj.keys()):
            dotted = f"{prefix}.{key}" if prefix else key
            key_counts[dotted] = key_counts.get(dotted, 0) + 1
            value = obj[key]
            if isinstance(value, dict):
                collect(value, dotted)

    for note_path in iter_markdown_files(root):
        files_scanned += 1
        note = _read_note(note_path)
        if note.errors:
            parse_errors += 1
            continue
        if note.frontmatter is None:
            continue
        files_with_frontmatter += 1
        collect(note.frontmatter)

    fields = [{"field": field, "count": key_counts[field]} for field in sorted(key_counts.keys())]
    return {
        "summary": {
            "files_scanned": files_scanned,
            "files_with_frontmatter": files_with_frontmatter,
            "parse_errors": parse_errors,
            "distinct_fields": len(fields),
        },
        "fields": fields,
    }
