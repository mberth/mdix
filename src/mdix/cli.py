from __future__ import annotations

import inspect
import json
import sys
from datetime import date, datetime
from importlib.resources import files
from pathlib import Path
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

import click
import yaml

from .frontmatter_io import format_frontmatter_yaml, read_frontmatter
from .schema import MigrationOperation, inventory_vault, load_contract, migrate_vault, normalize_vault, validate_vault
from .vault import iter_markdown_files

CLI_HELP = """Agent-friendly Markdown toolkit for deterministic vault automation.

`mdix` reads and updates Markdown vaults where frontmatter quality matters.
Default output is machine-friendly JSON so coding agents can pipe to `jq`,
parse with scripts, and make decisions from stable structures.
"""

CLI_EPILOG = """\b
Quick usage:
  mdix [--root <vault>] <command> [options]

\b
Global behavior:
  - Default output is machine-friendly JSON.
  - Use --human to force terminal-friendly text output where supported.
  - Set --root once (or MDIX_ROOT) to scope all commands to a vault.

\b
Command guide:
  ls                 List markdown files (optional frontmatter presence filter).
  find <query>       Search raw note text and return path/line matches.
  q                  Index all notes as JSON: path, frontmatter, parse errors.
  fm show <path>     Parse and report frontmatter for one file.
  fm normalize       Apply deterministic metadata normalization transforms.
                     Configure operations with --map-value, --set-default, etc.
  schema inventory   Report observed frontmatter fields and counts.
  schema validate    Validate notes against mdix.schema.yml.
  schema migrate     Apply ordered schema migration rules from mdix.schema.yml.

\b
Automation patterns:
  - detect malformed frontmatter:
    mdix q --fail-on-errors
  - validate one sub-tree:
    mdix schema validate --include "people/**"
  - preview migration safely:
    mdix schema migrate --dry-run
  - inspect one note's metadata:
    mdix fm show people/albert-einstein.md

\b
Exit codes to rely on in agents/CI:
  - q --fail-on-errors exits 2 when any note has parse errors.
  - find exits 1 when there are no matches.
  - schema validate exits 2 on violations in strict mode (default).

\b
Help drill-down:
  mdix <command> --help
  mdix fm --help
  mdix schema --help
"""

FM_HELP = """Frontmatter operations for inspection and deterministic normalization."""

FM_EPILOG = """\b
Quick usage:
  mdix fm <command> [options]

\b
Recommended workflow:
  - inspect one file with `fm show` before bulk edits
  - preview bulk edits with `fm normalize --dry-run`
  - apply the same normalize command without `--dry-run`

\b
Commands:
  show <path>         Parse one note and return frontmatter + parse errors.
  normalize ...       Apply deterministic normalization operations across files.
  set / unset / lint  Reserved command names; not implemented yet.

\b
Normalization operations (repeatable where noted):
  --map-value FIELD FROM TO
  --set-default FIELD VALUE
  --derive TARGET SOURCE
  --derive-from-filename FIELD
  --unset-if-null FIELD
  --remove-null-keys

\b
Examples:
  mdix fm show people/marie-curie.md
  mdix fm normalize --dry-run --remove-null-keys
  mdix fm normalize --set-default type person

\b
Output behavior:
  - default output is machine-friendly JSON
  - use global `--human` (or command-level `--human` where supported) for text
  - `fm normalize` supports `--human` and `--json` overrides
"""

SCHEMA_HELP = """Schema contract commands for field inventory, validation, and migration."""

SCHEMA_EPILOG = """\b
Quick usage:
  mdix schema <command> [options]

\b
Contract file:
  - default schema path: <root>/mdix.schema.yml
  - override with: --schema-path <file>

\b
Schema file format (`mdix.schema.yml`):
  - top-level keys: `version`, `fields`, optional `migrations`
  - `fields.<name>` supports constraints like:
    - `type`: string | integer | number | boolean | array | object
    - `required`: true/false
    - `enum`: [allowed, values]
  - `migrations` is an ordered list of transforms applied per note

\b
Migration operations (`migrations` entries):
  - rename:
      op: rename
      from: legacy.field
      to: canonical.field
  - value_map:
      op: value_map
      field: status
      map: {active: identified, stale: archived}
  - set_default:
      op: set_default
      field: type
      value: person
  - unset_if_null:
      op: unset_if_null
      field: legacy_note

\b
Migration behavior guarantees:
  - operations run in listed order for each in-scope markdown file
  - only files with frontmatter are candidates for migration
  - parse errors are reported as `parse_error` and never overwritten
  - `rename` only runs when `from` exists and `to` does not exist
  - `set_default` runs only when the field is missing or null
  - `--dry-run` returns deterministic previews without writing files

\b
Minimal example:
  version: 1
  fields:
    title:
      type: string
      required: true
    type:
      type: string
      required: true
      enum: [person, discovery, media, subject]
  migrations:
    - op: rename
      from: rolle
      to: position
    - op: value_map
      field: status
      map:
        active: identified
    - op: set_default
      field: type
      value: person
    - op: unset_if_null
      field: legacy_note

\b
Commands:
  inventory           Report observed frontmatter fields and usage counts.
  validate            Check notes against schema rules and enum/required fields.
  migrate             Apply schema-defined migration operations (safe with dry-run).

\b
Agent/CI workflow:
  1) mdix schema inventory
  2) mdix schema validate --include "people/*"
  3) mdix schema migrate --dry-run --include "people/*"
  4) mdix schema migrate --include "people/*"
  5) mdix schema validate --include "people/*"

\b
Exit codes to rely on:
  - `schema validate` exits 2 on violations in strict mode (default)
  - `schema validate --no-strict` reports violations but does not fail on them

\b
Examples:
  mdix schema inventory
  mdix schema validate --include "people/*"
  mdix schema migrate --dry-run
"""


def _relpath_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _emit(value: Any, *, human: bool) -> None:
    if human:
        if isinstance(value, list):
            for item in value:
                click.echo(str(item))
        else:
            click.echo(str(value))
        return

    click.echo(json.dumps(value, sort_keys=True, ensure_ascii=False, default=_json_default))


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _resolve_human_mode(default_human: bool, human: bool, json_mode: bool) -> bool:
    if human and json_mode:
        raise click.ClickException("Choose at most one of --human or --json.")
    if human:
        return True
    if json_mode:
        return False
    return default_human


def _summarize_q_errors(items: list[dict[str, Any]]) -> list[str]:
    errored = [item for item in items if item.get("errors")]
    if not errored:
        return []

    lines = [f"q strict mode: found parse errors in {len(errored)} note(s)"]
    for item in errored:
        path = str(item.get("path", "<unknown>"))
        types = sorted(
            {str(err.get("type", "unknown_error")) for err in item.get("errors", []) if isinstance(err, dict)}
        )
        type_summary = ", ".join(types) if types else "unknown_error"
        lines.append(f"- {path}: {type_summary}")
    return lines


def _path_in_scope(rel_path: str, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    path = PurePosixPath(rel_path)
    if include and not any(path.match(pattern) for pattern in include):
        return False
    if exclude and any(path.match(pattern) for pattern in exclude):
        return False
    return True


def _parse_yaml_value(value: str, *, option_name: str) -> Any:
    try:
        return yaml.safe_load(value)
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML value for {option_name}: {e}") from e


def _not_implemented(_: click.Context, __: click.Parameter, value: bool) -> bool:
    # Placeholder for future global flags; keeps API stable.
    return value


class MdixGroup(click.Group):
    """Render full command summaries in help instead of truncating with ellipses."""

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        rows: list[tuple[str, str]] = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue

            help_text = inspect.cleandoc(cmd.help or cmd.short_help or "").strip()
            if help_text:
                # Keep the first logical paragraph, then let Click wrap naturally.
                help_text = " ".join(help_text.split("\n\n", maxsplit=1)[0].splitlines())
            rows.append((subcommand, help_text))

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)


@click.group(
    cls=MdixGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=CLI_HELP,
    epilog=CLI_EPILOG,
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd,
    envvar="MDIX_ROOT",
    show_default="cwd / MDIX_ROOT",
    help="Vault root directory (defaults to cwd, or MDIX_ROOT).",
)
@click.option(
    "--human/--no-human",
    default=False,
    is_eager=True,
    expose_value=True,
    callback=_not_implemented,
    help="Opt in to human-readable output (default is machine-friendly).",
)
@click.pass_context
def cli(ctx: click.Context, root: Path, human: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["root"] = root.resolve()
    ctx.obj["human"] = human


@cli.command(help="List markdown files under the vault root.")
@click.option(
    "--has",
    "has_filter",
    type=str,
    default=None,
    help='Filter by presence, e.g. "--has fm.tags" (top-level frontmatter key).',
)
@click.pass_context
def ls(ctx: click.Context, has_filter: str | None) -> None:
    root: Path = ctx.obj["root"]
    human: bool = ctx.obj["human"]

    fm_key: str | None = None
    if has_filter is not None:
        if not has_filter.startswith("fm.") or len(has_filter) <= 3:
            raise click.ClickException('Invalid --has filter. Expected "fm.<field>".')
        fm_key = has_filter.removeprefix("fm.")

    paths: list[str] = []
    for p in iter_markdown_files(root):
        if fm_key is not None:
            fm_read = read_frontmatter(p)
            if fm_read.errors:
                rel = _relpath_posix(p, root)
                msg = fm_read.errors[0].get("message", "unknown error")
                raise click.ClickException(f"Malformed frontmatter in {rel}: {msg}")
            if fm_read.frontmatter is None or fm_key not in fm_read.frontmatter:
                continue

        paths.append(_relpath_posix(p, root))
    _emit(paths, human=human)


@cli.command(help="Query/index notes (JSON dump for downstream jq).")
@click.option(
    "--fail-on-errors",
    "--strict",
    "fail_on_errors",
    is_flag=True,
    default=False,
    help="Exit non-zero when any note has parse errors; still prints full JSON to stdout.",
)
@click.pass_context
def q(ctx: click.Context, fail_on_errors: bool) -> None:
    root: Path = ctx.obj["root"]
    human: bool = ctx.obj["human"]

    if human:
        raise click.ClickException("Human output is not implemented for `q` yet (use default JSON).")

    items: list[dict[str, Any]] = []
    for p in iter_markdown_files(root):
        rel = _relpath_posix(p, root)
        fm_read = read_frontmatter(p)
        items.append(
            {
                "path": rel,
                "frontmatter": fm_read.frontmatter,
                "errors": fm_read.errors,
            }
        )

    _emit(items, human=False)
    if fail_on_errors:
        summary_lines = _summarize_q_errors(items)
        if summary_lines:
            click.echo("\n".join(summary_lines), err=True)
            ctx.exit(2)


@cli.command(help="Quick text search across markdown files.")
@click.argument("query", required=True)
@click.pass_context
def find(ctx: click.Context, query: str) -> None:
    root: Path = ctx.obj["root"]
    human: bool = ctx.obj["human"]

    matches: list[dict[str, Any]] = []
    for p in iter_markdown_files(root):
        rel = _relpath_posix(p, root)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise click.ClickException(f"Failed to read {rel} as utf-8: {e}") from e

        for i, line in enumerate(text.splitlines(), start=1):
            if query in line:
                matches.append({"path": rel, "line": i, "text": line})

    if not matches:
        # Stable: 1 means "no matches" (not an error reading files).
        ctx.exit(1)

    if human:
        for m in matches:
            click.echo(f"{m['path']}:{m['line']}: {m['text']}")
        return

    _emit(matches, human=False)


_DEMO_VAULTS: dict[str, str] = {
    "great-discoveries": "vault_great_discoveries",
    "energy-storage": "energy_storage",
}

_DEMO_NEXT_STEPS: dict[str, list[str]] = {
    "great-discoveries": [
        "uvx mdix find relativity",
        "uvx mdix ls --has fm.status",
        "uvx mdix q | jq '[.[] | select((.errors | length) > 0) | {path, errors}]'",
    ],
    "energy-storage": [
        "uvx mdix find lithium",
        "uvx mdix schema validate",
        "uvx mdix schema inventory --human",
    ],
}


def _copy_tree(src: "Traversable", dest: Path) -> None:
    """Recursively copy a Traversable (works for both installed packages and editable installs)."""
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name == "__init__.py":
            continue
        if item.is_dir():
            _copy_tree(item, dest / item.name)
        else:
            (dest / item.name).write_bytes(item.read_bytes())


@cli.command(help="Copy a demo vault to a local directory for experimentation.")
@click.argument("vault", required=False, metavar="VAULT")
@click.option(
    "--dest",
    type=click.Path(path_type=Path),
    default=None,
    help="Destination directory (default: ./<vault-name>).",
)
def demo(vault: str | None, dest: Path | None) -> None:
    if vault is None:
        click.echo("Available demo vaults:\n")
        for name, folder in _DEMO_VAULTS.items():
            src = files("mdix") / "_examples" / folder
            count = sum(1 for _ in src.iterdir() if not str(_).endswith("__init__.py"))
            click.echo(f"  {name:<22}  {count} top-level items")
        click.echo("\nUsage: uvx mdix demo <vault-name>")
        return

    if vault not in _DEMO_VAULTS:
        names = ", ".join(_DEMO_VAULTS)
        raise click.ClickException(f"Unknown vault '{vault}'. Choose one of: {names}")

    folder = _DEMO_VAULTS[vault]
    target = dest if dest is not None else Path.cwd() / vault

    if target.exists():
        raise click.ClickException(
            f"Destination already exists: {target}\nRemove it first, or use --dest to pick a different path."
        )

    src = files("mdix") / "_examples" / folder
    _copy_tree(src, target)

    click.echo(f"Demo vault copied to: {target}\n")
    click.echo("Get started:")
    click.echo(f"  cd {target}")
    for cmd in _DEMO_NEXT_STEPS.get(vault, []):
        click.echo(f"  {cmd}")


@cli.group(cls=MdixGroup, help=FM_HELP, epilog=FM_EPILOG)
def fm() -> None:
    pass


@fm.command(name="show", help="Parse and display YAML frontmatter for a single file.")
@click.argument("path", required=True)
@click.pass_context
def fm_show(ctx: click.Context, path: str) -> None:
    root: Path = ctx.obj["root"]
    human: bool = ctx.obj["human"]

    full_path = (root / path).resolve()
    try:
        full_path.relative_to(root)
    except ValueError as e:
        raise click.ClickException("Path must be under the vault root.") from e

    if not full_path.exists() or not full_path.is_file():
        raise click.ClickException(f"File not found: {path}")

    fm_read = read_frontmatter(full_path)
    rel = _relpath_posix(full_path, root)

    if human:
        if fm_read.errors:
            raise click.ClickException(fm_read.errors[0].get("message", "frontmatter parse error"))
        click.echo(format_frontmatter_yaml(fm_read.frontmatter), nl=False)
        return

    _emit(
        {
            "path": rel,
            "frontmatter": fm_read.frontmatter,
            "errors": fm_read.errors,
        },
        human=False,
    )


@fm.command(name="set", help="Not yet implemented.")
@click.pass_context
def fm_set(ctx: click.Context) -> None:  # noqa: ARG001 - ctx for consistent signature
    raise click.ClickException("Not yet implemented")


@fm.command(name="unset", help="Not yet implemented.")
@click.pass_context
def fm_unset(ctx: click.Context) -> None:  # noqa: ARG001 - ctx for consistent signature
    raise click.ClickException("Not yet implemented")


@fm.command(name="lint", help="Not yet implemented.")
@click.pass_context
def fm_lint(ctx: click.Context) -> None:  # noqa: ARG001 - ctx for consistent signature
    raise click.ClickException("Not yet implemented")


@fm.command(name="normalize", help="Batch-normalize frontmatter with deterministic preview/apply output.")
@click.option(
    "--include",
    "include_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to include (repeatable, matched relative to --root).",
)
@click.option(
    "--exclude",
    "exclude_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to exclude (repeatable, matched relative to --root).",
)
@click.option(
    "--map-value",
    "map_values",
    nargs=3,
    multiple=True,
    metavar="FIELD FROM TO",
    help="Map a field value (repeatable). FROM/TO are parsed as YAML scalars.",
)
@click.option(
    "--set-default",
    "set_defaults",
    nargs=2,
    multiple=True,
    metavar="FIELD VALUE",
    help="Set default when field is missing/null (repeatable). VALUE is parsed as YAML.",
)
@click.option(
    "--derive",
    "derives",
    nargs=2,
    multiple=True,
    metavar="TARGET SOURCE",
    help="Set TARGET from SOURCE when TARGET is missing/null.",
)
@click.option(
    "--derive-from-filename",
    "derive_from_filename",
    multiple=True,
    metavar="FIELD",
    help="Set FIELD from note filename when FIELD is missing/null.",
)
@click.option(
    "--unset-if-null",
    "unset_if_null",
    multiple=True,
    metavar="FIELD",
    help="Remove FIELD when its value is null.",
)
@click.option(
    "--remove-null-keys",
    is_flag=True,
    default=False,
    help="Recursively remove all frontmatter keys with null values.",
)
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing files.")
@click.option("--human", "human_mode", is_flag=True, default=False, help="Force human-readable output.")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Force JSON output.")
@click.pass_context
def fm_normalize(
    ctx: click.Context,
    include_patterns: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
    map_values: tuple[tuple[str, str, str], ...],
    set_defaults: tuple[tuple[str, str], ...],
    derives: tuple[tuple[str, str], ...],
    derive_from_filename: tuple[str, ...],
    unset_if_null: tuple[str, ...],
    remove_null_keys: bool,
    dry_run: bool,
    human_mode: bool,
    json_mode: bool,
) -> None:
    root: Path = ctx.obj["root"]
    default_human: bool = ctx.obj["human"]
    human = _resolve_human_mode(default_human, human_mode, json_mode)

    operations: list[MigrationOperation] = []
    for field, source_raw, target_raw in map_values:
        source_value = _parse_yaml_value(source_raw, option_name="--map-value FROM")
        target_value = _parse_yaml_value(target_raw, option_name="--map-value TO")
        operations.append(MigrationOperation(op="value_map", field=field, mapping=((source_value, target_value),)))
    for field, value_raw in set_defaults:
        operations.append(
            MigrationOperation(
                op="set_default", field=field, value=_parse_yaml_value(value_raw, option_name="--set-default")
            )
        )
    for target, source in derives:
        operations.append(MigrationOperation(op="derive", field=target, source=source))
    for field in derive_from_filename:
        operations.append(MigrationOperation(op="derive_from_filename", field=field))
    for field in unset_if_null:
        operations.append(MigrationOperation(op="unset_if_null", field=field))
    if remove_null_keys:
        operations.append(MigrationOperation(op="remove_null_keys"))

    if not operations:
        raise click.ClickException(
            "No operations configured. Use one of --map-value/--set-default/--derive/--derive-from-filename/"
            "--unset-if-null/--remove-null-keys."
        )

    result = normalize_vault(
        root,
        operations=tuple(operations),
        include=include_patterns,
        exclude=exclude_patterns,
        dry_run=dry_run,
    )
    if not human:
        _emit(result, human=False)
        return

    summary = result["summary"]
    click.echo(
        (
            f"files_scanned={summary['files_scanned']} "
            f"files_changed={summary['files_changed']} "
            f"operations={summary['operations']} "
            f"parse_errors={summary['parse_errors']} "
            f"dry_run={summary['dry_run']}"
        )
    )
    for item in result["changes"]:
        if item["status"] == "parse_error":
            click.echo(f"- {item['path']} [parse_error]")
            continue
        for change in item["changes"]:
            op = change["op"]
            if op == "value_map":
                click.echo(f"- {item['path']} value_map {change['field']}: {change['from']} -> {change['to']}")
            elif op == "set_default":
                click.echo(f"- {item['path']} set_default {change['field']} = {change['value']}")
            elif op == "derive":
                click.echo(f"- {item['path']} derive {change['field']} <- {change['from']}")
            elif op == "derive_from_filename":
                click.echo(f"- {item['path']} derive_from_filename {change['field']} = {change['value']}")
            elif op == "unset_if_null":
                click.echo(f"- {item['path']} unset_if_null {change['field']}")
            elif op == "remove_null_keys":
                click.echo(f"- {item['path']} remove_null_keys {', '.join(change['fields'])}")


@cli.command(help="Not yet implemented (planned: create new note from template).")
@click.pass_context
def new(ctx: click.Context) -> None:  # noqa: ARG001 - ctx for consistent signature
    raise click.ClickException("Not yet implemented")


@cli.group(cls=MdixGroup, help=SCHEMA_HELP, epilog=SCHEMA_EPILOG)
def schema() -> None:
    pass


@schema.command(help="Inventory frontmatter field usage across the vault.")
@click.option("--human", "human_mode", is_flag=True, default=False, help="Force human-readable output.")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Force JSON output.")
@click.pass_context
def inventory(ctx: click.Context, human_mode: bool, json_mode: bool) -> None:
    root: Path = ctx.obj["root"]
    default_human: bool = ctx.obj["human"]
    human = _resolve_human_mode(default_human, human_mode, json_mode)

    result = inventory_vault(root)
    if not human:
        _emit(result, human=False)
        return

    summary = result["summary"]
    click.echo(
        (
            f"files_scanned={summary['files_scanned']} "
            f"files_with_frontmatter={summary['files_with_frontmatter']} "
            f"parse_errors={summary['parse_errors']} "
            f"distinct_fields={summary['distinct_fields']}"
        )
    )
    for field in result["fields"]:
        click.echo(f"- {field['field']}: {field['count']}")


@schema.command(help="Validate vault frontmatter against the schema contract.")
@click.option(
    "--schema-path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to schema contract file (default: <root>/mdix.schema.yml).",
)
@click.option(
    "--include",
    "include_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to include (repeatable, matched relative to --root).",
)
@click.option(
    "--exclude",
    "exclude_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to exclude (repeatable, matched relative to --root).",
)
@click.option("--strict/--no-strict", default=True, help="Exit non-zero when violations are found.")
@click.option("--human", "human_mode", is_flag=True, default=False, help="Force human-readable output.")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Force JSON output.")
@click.pass_context
def validate(
    ctx: click.Context,
    schema_path: Path | None,
    include_patterns: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
    strict: bool,
    human_mode: bool,
    json_mode: bool,
) -> None:
    root: Path = ctx.obj["root"]
    default_human: bool = ctx.obj["human"]
    human = _resolve_human_mode(default_human, human_mode, json_mode)

    resolved_schema = schema_path.resolve() if schema_path is not None else (root / "mdix.schema.yml").resolve()
    if not resolved_schema.exists():
        raise click.ClickException(f"Schema file not found: {resolved_schema}")

    try:
        contract = load_contract(resolved_schema)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    result = validate_vault(root, contract, include=include_patterns, exclude=exclude_patterns)

    if not human:
        _emit(result, human=False)
    else:
        click.echo(f"schema={result['schema']}")
        summary = result["summary"]
        click.echo(
            (
                f"files_scanned={summary['files_scanned']} "
                f"files_with_frontmatter={summary['files_with_frontmatter']} "
                f"files_validated={summary['files_validated']} "
                f"files_valid={summary['files_valid']} "
                f"files_with_violations={summary['files_with_violations']} "
                f"parse_errors={summary['parse_errors']} "
                f"violations={summary['violations']}"
            )
        )
        for violation in result["violations"]:
            field = violation["field"] if violation["field"] is not None else "-"
            click.echo(f"- {violation['path']} [{violation['code']}] {field}: {violation['message']}")

    if strict and result["summary"]["violations"] > 0:
        ctx.exit(2)


@schema.command(help="Migrate legacy frontmatter keys into canonical schema keys.")
@click.option(
    "--schema-path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to schema contract file (default: <root>/mdix.schema.yml).",
)
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing files.")
@click.option(
    "--include",
    "include_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to include (repeatable, matched relative to --root).",
)
@click.option(
    "--exclude",
    "exclude_patterns",
    type=str,
    multiple=True,
    help="Glob pattern for paths to exclude (repeatable, matched relative to --root).",
)
@click.option("--human", "human_mode", is_flag=True, default=False, help="Force human-readable output.")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Force JSON output.")
@click.pass_context
def migrate(
    ctx: click.Context,
    schema_path: Path | None,
    dry_run: bool,
    include_patterns: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
    human_mode: bool,
    json_mode: bool,
) -> None:
    root: Path = ctx.obj["root"]
    default_human: bool = ctx.obj["human"]
    human = _resolve_human_mode(default_human, human_mode, json_mode)

    resolved_schema = schema_path.resolve() if schema_path is not None else (root / "mdix.schema.yml").resolve()
    if not resolved_schema.exists():
        raise click.ClickException(f"Schema file not found: {resolved_schema}")

    try:
        contract = load_contract(resolved_schema)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    result = migrate_vault(
        root,
        contract,
        include=include_patterns,
        exclude=exclude_patterns,
        dry_run=dry_run,
    )
    if not human:
        _emit(result, human=False)
        return

    click.echo(f"schema={result['schema']}")
    summary = result["summary"]
    click.echo(
        (
            f"files_scanned={summary['files_scanned']} "
            f"files_changed={summary['files_changed']} "
            f"operations={summary['operations']} "
            f"parse_errors={summary['parse_errors']} "
            f"dry_run={summary['dry_run']}"
        )
    )
    for item in result["changes"]:
        if item["status"] == "parse_error":
            click.echo(f"- {item['path']} [parse_error]")
            continue
        for change in item["changes"]:
            op = change["op"]
            if op == "rename":
                click.echo(f"- {item['path']} rename {change['from']} -> {change['to']}")
            elif op == "value_map":
                click.echo(f"- {item['path']} value_map {change['field']}: {change['from']} -> {change['to']}")
            elif op == "set_default":
                click.echo(f"- {item['path']} set_default {change['field']} = {change['value']}")
            elif op == "unset_if_null":
                click.echo(f"- {item['path']} unset_if_null {change['field']}")


def main() -> None:
    try:
        cli()
    except BrokenPipeError:
        # E.g. piping to `head` should not throw stack traces.
        sys.exit(0)
