from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

from .frontmatter_io import format_frontmatter_yaml, read_frontmatter
from .schema import inventory_vault, load_contract, migrate_vault, validate_vault
from .vault import iter_markdown_files


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

    click.echo(json.dumps(value, sort_keys=True, ensure_ascii=False))


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
            {
                str(err.get("type", "unknown_error"))
                for err in item.get("errors", [])
                if isinstance(err, dict)
            }
        )
        type_summary = ", ".join(types) if types else "unknown_error"
        lines.append(f"- {path}: {type_summary}")
    return lines


def _not_implemented(_: click.Context, __: click.Parameter, value: bool) -> bool:
    # Placeholder for future global flags; keeps API stable.
    return value


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
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
    """Agent-friendly Markdown toolkit."""
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


@cli.group(help="Frontmatter operations (show/set/unset/lint).")
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


@cli.command(help="Not yet implemented (planned: create new note from template).")
@click.pass_context
def new(ctx: click.Context) -> None:  # noqa: ARG001 - ctx for consistent signature
    raise click.ClickException("Not yet implemented")


@cli.group(help="Vault schema contract commands (inventory/validate/migrate).")
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
@click.option("--human", "human_mode", is_flag=True, default=False, help="Force human-readable output.")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Force JSON output.")
@click.pass_context
def migrate(
    ctx: click.Context,
    schema_path: Path | None,
    dry_run: bool,
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

    result = migrate_vault(root, contract, dry_run=dry_run)
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
            click.echo(f"- {item['path']} rename {change['from']} -> {change['to']}")


def main() -> None:
    try:
        cli()
    except BrokenPipeError:
        # E.g. piping to `head` should not throw stack traces.
        sys.exit(0)

