# mdix - Agent-friendly Markdown Toolkit

`mdix` is a CLI for Markdown knowledge bases that humans and AI agents edit together.
It helps you search, validate, and normalize frontmatter in a way that stays predictable over time.

If you have ever ended up with mixed filename styles, drifting frontmatter keys, and inconsistent
frontmatter values, this tool is for you.


## Who it is for

- People and agents building knowledge bases on top of Markdown vaults
- Teams enforcing frontmatter contracts across many files
- Agent and automation workflows that need stable output and exit codes

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pipx`/`pip`
- [`jq`](https://jqlang.org/) (optional, used in examples to filter JSON output)

## Installation

### Recommended: run with `uvx` (no install)

```bash
uvx mdix --help
uvx mdix --root ~/notes find "search term"
```

### Install as a tool

```bash
uv tool install mdix
# or
pipx install mdix
# or
pip install --user mdix
```

## Quick start

No git clone needed. Download a demo vault and start exploring:

```bash
# Copy a demo vault to your current directory
uvx mdix demo great-discoveries
cd great-discoveries

# Text search across notes
uvx mdix find relativity

# List notes that have a specific frontmatter key
uvx mdix ls --has fm.status

# Query all notes as JSON; filter with jq to show only those with errors
uvx mdix q | jq '[.[] | select((.errors | length) > 0) | {path, errors}]'
```

There is also an energy storage vault (17 notes with a schema and agent instructions):

```bash
uvx mdix demo energy-storage
cd energy-storage

uvx mdix schema validate --human
uvx mdix schema inventory --human
```

See `INSTRUCTIONS.md` in that vault for the entry point an agent would use.

## Commands

| Command | What it does |
|---|---|
| `mdix q` | Index all notes as JSON (`path`, `frontmatter`, `errors`). YAML dates are serialized as ISO-8601. Add `--fail-on-errors` / `--strict` to exit non-zero on parse errors. |
| `mdix find <text>` | Full-text search across notes |
| `mdix ls` | List notes, optionally filtered by frontmatter keys (`--has fm.status`) |
| `mdix fm show <path>` | Inspect frontmatter on one note |
| `mdix fm normalize` | Batch frontmatter normalization: value remapping, defaults, derived fields, null-key removal. Always supports `--dry-run`. |
| `mdix schema inventory` | Frontmatter key inventory and drift visibility across the vault |
| `mdix schema validate` | Check notes against `mdix.schema.yml`. Exits `2` on violations. Supports `--include`/`--exclude` glob filters. |
| `mdix schema migrate` | Apply key/value/default/null migrations defined in the schema. Supports `--dry-run` and `--include`/`--exclude`. |

**Read-only commands** (never write files): `q`, `find`, `ls`, `fm show`, `schema inventory`, `schema validate`, and any command with `--dry-run`.

**Commands that write files**: `fm normalize` (without `--dry-run`), `schema migrate` (without `--dry-run`).

Full help:

```bash
mdix --help
mdix <command> --help
```

## Schema contract (`mdix.schema.yml`)

Place an `mdix.schema.yml` in your vault root (or pass `--schema-path`):

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
  - op: value_map
    field: status
    map:
      active: identified
  - op: set_default
    field: type
    value: person
  - op: unset_if_null
    field: legacy_note
```

Then validate and migrate:

```bash
mdix --root ~/notes schema validate
mdix --root ~/notes schema migrate --dry-run
mdix --root ~/notes schema migrate
```

## Agent-friendly output

- Machine-parseable JSON for automation (`jq`, CI, scripts)
- Human-readable output for interactive terminal usage
- Stable ordering for reproducible automation

```bash
mdix q | jq 'length'
```

## Going further

- [docs/workflows.md](docs/workflows.md) - Incremental cleanup patterns, scoped migration recipes, CI gates
- [docs/why.md](docs/why.md) - Background on the problem this solves


## Roadmap

- Richer batch-edit workflows with preview
- Document-outline and structural reading helpers for long notes

## Status

Early-stage.

## License

MIT
