# mdix - Agent-friendly Markdown Toolkit

`mdix` is a CLI for Markdown vaults (`*.md` files with optional YAML frontmatter).
It helps you search, validate, and normalize metadata safely and repeatably.

Use it when your vault has drifted frontmatter and you want deterministic cleanup instead of one-off scripts.

## Why mdix

- Deterministic output and ordering for reproducible CI and agent workflows
- JSON-first command output that composes cleanly with `jq`, `rg`, and shell pipelines
- Dry-run-first schema migration and frontmatter normalization
- Editor-agnostic behavior (works well with Obsidian-style vaults, not tied to Obsidian)

## Who it is for

- Maintainers of Markdown knowledge bases and note vaults
- Teams enforcing frontmatter contracts across many files
- Agent and automation workflows that need stable output and exit codes

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

## 2-minute quick start

By default, `mdix` searches the current working directory and subdirectories.
Point it at your vault with `--root` or `MDIX_ROOT`.

```bash
# Optional: set vault root once
export MDIX_ROOT=~/notes

# 1) Inspect current state
mdix schema validate | jq '.summary'

# 2) Preview normalization (no writes)
mdix fm normalize --dry-run \
  --include "people/**" \
  --map-value status active identified \
  --set-default type person \
  --derive title nickname \
  --remove-null-keys

# 3) Apply the same pass when preview looks right
mdix fm normalize \
  --include "people/**" \
  --map-value status active identified \
  --set-default type person \
  --derive title nickname \
  --remove-null-keys
```

For smaller tasks:

```bash
mdix find "attention is all you need"
mdix ls --has fm.tags
mdix q --fail-on-errors
mdix fm show path/to/note.md
```

`mdix q` JSON output normalizes YAML `date`/`datetime` scalar values to ISO-8601 strings so output stays valid for `jq` and CI pipelines.

## Core workflow: validate -> dry-run -> apply

Use this pattern for safe cleanup passes and reviewable commits:

```bash
mdix --root ~/notes schema inventory
mdix --root ~/notes schema validate --include "people/**" --exclude "people/archive/**"
mdix --root ~/notes schema migrate --dry-run --include "people/**"
mdix --root ~/notes schema migrate --include "people/**"
mdix --root ~/notes schema validate --include "people/**"
```

Both `schema validate` and `schema migrate` report the effective schema source path in output under `schema`.

## Vault cleanup tips (incremental workflow)

For mixed-content vaults, use small scoped cleanup steps and commit after each step:

```bash
# 1) Inventory drift first
mdix --root ~/notes schema inventory | jq '.summary'

# 2) Validate only the target collection
mdix --root ~/notes schema validate \
  --include "Personen/**" \
  --exclude "Personen/_TEMPLATE.md"

# 3) Preview and apply scoped migrations
mdix --root ~/notes schema migrate --dry-run --include "Personen/**"
mdix --root ~/notes schema migrate

# 4) Re-validate, then commit that single cleanup step
mdix --root ~/notes schema validate --include "Personen/**"
```

Practical notes:

- Prefer scoping with `--include`/`--exclude` to avoid noisy violations outside the current cleanup target.
- Use `schema migrate --dry-run` before writes and keep each migration pass as a separate commit.
- Use `fm normalize --dry-run` for repeatable status/title/type/null cleanup flows instead of ad-hoc scripts.
- Keep schema enums strict, then normalize legacy values in dedicated follow-up commits.
- Use a frontmatter library (for example `python-frontmatter`) or `mdix` helpers for scripted edits; avoid ad-hoc delimiter parsing.

### Real-world pattern: cleanup with focused commits

When a vault has mixed entity types and legacy metadata, `mdix` works well as a deterministic cleanup engine:

```bash
# 1) Start with a baseline
mdix --root ~/notes schema validate | jq '.summary'

# 2) Run a narrow, deterministic normalization pass (dry-run first)
mdix --root ~/notes fm normalize --dry-run \
  --include "Organisations/**" \
  --map-value status is_identified identified \
  --set-default type organisation \
  --derive title name \
  --remove-null-keys

# 3) Apply that one pass and commit only that slice
mdix --root ~/notes fm normalize \
  --include "Organisations/**" \
  --map-value status is_identified identified \
  --set-default type organisation \
  --derive title name \
  --remove-null-keys

# 4) Run a second independent pass (for example null-key cleanup)
mdix --root ~/notes fm normalize \
  --include "People/**" \
  --exclude "People/_TEMPLATE.md" \
  --remove-null-keys
```

Why this helps:

- Each pass is scoped and reviewable.
- Dry-run and apply use the same command shape, reducing operator error.
- Git history stays meaningful because each commit captures one cleanup intention.
- You can re-run `schema validate` between passes to measure progress without touching unrelated areas.

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
  - YAML `date`/`datetime` scalars are serialized as ISO-8601 strings in JSON output
- `mdix find` - quick text search
- `mdix fm show` - frontmatter inspection
- `mdix fm normalize` - deterministic batch frontmatter normalization with dry-run preview
- `mdix schema inventory` - frontmatter key inventory and drift visibility
- `mdix schema validate` - deterministic schema violations for CI/local gates (exit code `2` on violations in strict mode), scoped to files with parseable frontmatter
  - supports repeatable `--include` and `--exclude` glob filters for path scoping
- `mdix schema migrate` - safe key/value/default/null migration transforms with dry-run preview
  - supports repeatable `--include` and `--exclude` glob filters for path scoping

## Epic 17 motivating vault pointer

Epic 17 examples target a repository-local pointer at `tmp/ai-barcamp-greifswald`.

- The pointer is optional and read-only for validation/migration dry-runs.
- Local setup assumes the motivating vault is available at `../ai-barcamp-greifswald` relative to this repo (for example `/Users/<you>/work/ai-barcamp-greifswald`).
- Recreate the pointer with:

```bash
ln -sfn ../../ai-barcamp-greifswald tmp/ai-barcamp-greifswald
```

- Verify setup (fails fast with a clear message when broken):

```bash
scripts/check-epic17-vault.sh
```

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
