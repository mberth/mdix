from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

from .frontmatter_io import format_frontmatter_yaml, read_frontmatter
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


def main() -> None:
    try:
        cli()
    except BrokenPipeError:
        # E.g. piping to `head` should not throw stack traces.
        sys.exit(0)

