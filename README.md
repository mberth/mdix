# mdix - Agent-friendly Markdown Toolkit

**mdix** is a command-line interface for Markdown vaults: directory hierarchies of `*.md` files with optional YAML frontmatter.

It is built for agent workflows:

- predictable, scriptable commands
- machine-friendly output is the default, but you can use `--human`
- deterministic ordering for reproducibility
- editor-agnostic behavior, it works well with Obsidian-style vaults, but is not tied to Obsidian

## What's next

- search notes by text, path, and frontmatter filters
- inspect and manage frontmatter fields
- use stable output and exit codes in shell pipelines and CI


## Installation

### Recommended: run with `uvx` (no install)

If you already have `uv`, run `mdix` in an isolated environment:

```bash
uvx mdix --help
uvx mdix --root ~/notes find "backprop"
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

By default, mdix will search the current working directory and its subdirectories.

Later: Point `mdix` at a vault directory:

```bash
mdix --root ~/notes --help
```

Or set `MDIX_ROOT`


```bash
MDIX_ROOT=~/notes mdix --help
```


Search content:

```bash
mdix find "attention is all you need"
```

List notes that contain a frontmatter field:

```bash
mdix ls --has fm.tags
```

`--has fm.<field>` checks frontmatter key presence. Keys with `null` values still count as present.
To filter for non-null values, pipe `mdix q` into `jq`.

Query by metadata:

```bash
mdix q
```

Fail CI/jobs when parse errors are present, while still keeping JSON on stdout:

```bash
mdix q --fail-on-errors
```

Show frontmatter for a specific note:

```bash
mdix fm show path/to/note.md
```

Validate and migrate a vault schema contract:

```bash
mdix --root ~/notes schema inventory
mdix --root ~/notes schema validate
mdix --root ~/notes schema migrate --dry-run
mdix --root ~/notes schema migrate
```

## Agent-friendly output

- text output by default for interactive use
- json is the default for machine consumption
- stable ordering to support reproducible automation

Example:

```bash
mdix q | jq 'length'
```

## Commands

- `mdix q` - index/query notes as a JSON list (`path`, `frontmatter`, `errors`)
  - add `--fail-on-errors` (alias: `--strict`) to emit an error summary to stderr and exit non-zero when any item has `errors`
- `mdix find` - quick text search
- `mdix fm show` - frontmatter inspection
- `mdix schema inventory` - frontmatter key inventory and drift visibility
- `mdix schema validate` - deterministic schema violations for CI/local gates (exit code `2` on violations in strict mode)
- `mdix schema migrate` - safe key migration transforms with dry-run preview

## Schema contract (`mdix.schema.yml`)

Place an `mdix.schema.yml` in the vault root (or pass `--schema-path`):

```yaml
version: 1
fields:
  title:
    type: string
    required: true
  type:
    type: string
    required: true
    enum: [person, discovery, media, subject]
  position:
    type: string
  kontakt.email:
    type: string
migrations:
  - op: rename
    from: rolle
    to: position
  - op: rename
    from: kontakt_email
    to: kontakt.email
```

See command help:

```bash
mdix --help
mdix <command> --help
```

## Development

This project uses `uv` for dependency management.
The project supports Python `>=3.11` and CI runs on Python 3.11.

```bash
uv sync
uv run ruff check .
uv run pytest
```

## Roadmap

- richer batch-edit workflows with preview
- document-outline and structural reading helpers for long notes

## Design goals

- be a good unix utility
- agents first: machine readable output is the default, i.e. lines, json or jsonl
- easy to discover functionality
- composable: works well with `rg`, `jq`, `xargs`, and CI

## Status

Early-stage.

## License

MIT
