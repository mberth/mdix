# mdix - Agent-friendly Markdown toolkit

**mdix** is a command-line interface for Markdown vaults: directory hierarchies of `*.md` files with optional YAML frontmatter.

It is built for automation and agent workflows:

- predictable, scriptable commands
- machine-friendly output is the default, but you can suse `--human`
- deterministic ordering for reproducibility
- editor-agnostic behavior (works well with Obsidian-style vaults, but is not tied to Obsidian)

## What works today

- search notes by text, path, and frontmatter filters
- combine structured metadata filters with content search
- inspect and manage frontmatter fields
- use stable output and exit codes in shell pipelines and CI

Most query power lives in `mdix q`, while `find` and `ls` cover common fast paths.

## Installation

### Recommended: run with `uvx` (no install)

If you already have `uv`, run `mdix` in an isolated environment:

```bash
uvx mdix --help
uvx mdix --root ~/notes find "backprop" --json
```

### Install as a tool with `uv`

```bash
uv tool install mdix
mdix --help
```

### Fallback options: `pipx` / `pip`

```bash
pipx install mdix
# or
pip install --user mdix
```

## Quick start

Point `mdix` at a vault directory:

```bash
mdix --root ~/notes --help
```

Search content:

```bash
mdix --root ~/notes find "attention is all you need"
```

List notes that contain a frontmatter field:

```bash
mdix --root ~/notes ls --has fm.tags
```

Query by metadata:

```bash
mdix --root ~/notes q --where 'tags contains "ml"'
```

Combine metadata and text, then emit JSON:

```bash
mdix --root ~/notes q --where 'status == "active" and tags contains "ml"' --text "TODO" --json
```

Show frontmatter for a specific note:

```bash
mdix --root ~/notes fm show path/to/note.md
```

## Agent-friendly output

- text output by default for interactive use
- `--json` for machine consumption
- stable ordering to support reproducible automation

Example:

```bash
mdix --root ~/notes q --where 'tags contains "ml"' --json | jq '.results | length'
```

## Commands

- `mdix q` - query notes (frontmatter + content + path)
- `mdix find` - quick text search
- `mdix ls` - list with filters
- `mdix fm show|set|unset|lint` - frontmatter operations
- `mdix new` - create from template

See command help:

```bash
mdix --help
mdix <command> --help
```

## Development

This project uses `uv` for dependency management.

```bash
uv sync
uv run pytest
```

## Roadmap

- richer batch-edit workflows with preview
- document-outline and structural reading helpers for long notes

## Design principles

- files first: plain Markdown + YAML frontmatter
- query-first: vault-wide answers before edits
- safe writes: dry-run, diffs, explicit apply
- composable: works well with `rg`, `jq`, `xargs`, and CI

## Status

Early-stage.

## License

MIT
