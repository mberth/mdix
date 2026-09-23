# mdix - Agent-friendly Markdown Toolkit

`mdix` is a command-line toolkit that keeps Markdown knowledge bases consistent, especially when humans and AI agents maintain them together.

**The setup:** You keep a folder of Markdown files — one per entity — with YAML frontmatter for metadata. You browse and edit in Obsidian (or any editor), and an AI agent researches, creates, and curates notes alongside you. Git tracks history. Structure grows organically as you learn more about the subject.

**The problem:** Over time, this workflow accumulates drift. Filenames follow mixed conventions, frontmatter keys diverge (`type` vs `kind`, renamed fields that linger), value vocabularies become inconsistent (`active`, `identified`, `is_identified`), and partial metadata silently propagates into new notes. This makes agent behavior less reliable, search noisier, and automation harder to trust.

**What mdix does:** It gives the agent that works alongside you a command-line interface to search, validate, and normalize frontmattser across your vault, with dry-run previews, schema contracts, and stable machine-readable output. Tell your agent to run `mdix --help` and it can orient itself and start using mdix competently.

For more background, see [docs/why.md](docs/why.md).

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
uvx mdix links unresolved --human
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
| `mdix links ls` | List wikilink occurrences with the note each one resolves to (`--from`, `--unresolved-only`, `--include`/`--exclude`). |
| `mdix links resolve <target>` | Resolve one wikilink the way Obsidian would, from a given page (`--from`). Exits `1` when nothing matches. |
| `mdix links unresolved` | List link targets that have no note yet, ranked by how many notes link them. Supports `--include`/`--exclude`; `--subpaths` also lists missing `#Heading` and `#^block-id` targets. |

**Read-only commands** (never write files): `q`, `find`, `ls`, `fm show`, `schema inventory`, `schema validate`, `links ls`, `links resolve`, `links unresolved`, and any command with `--dry-run`.

**Commands that write files**: `fm normalize` (without `--dry-run`), `schema migrate` (without `--dry-run`).

Full help:

```bash
mdix --help
mdix <command> --help
```

## Wikilinks and the frontier

`mdix links` reads `[[wikilinks]]` the way Obsidian does, including relative paths, partial
paths, ambiguous names, frontmatter links and frontmatter aliases.

Resolve one link, from the page it is written in:

```bash
mdix links resolve "[[Fluence]]" --from projects/moss-landing.md
```

```json
{"target": "Fluence", "subpath": null, "display": null, "from": "projects/moss-landing.md",
 "resolved": "companies/fluence.md", "via": "basename", "candidates": ["companies/fluence.md"]}
```

`via` names the rule that matched (`exact_path`, `relative_path`, `path_suffix`, `basename`,
`alias`, `self`), and `candidates` lists every file the name could have meant, best match first.

The interesting list is the other one: the links that point at notes you have not written yet.
In a vault that grows outward from what is already there, that is the queue.

```bash
mdix links unresolved --human
```

```
3  thermal-runaway
   - concepts/cycle-life.md
   - technologies/lithium-ion-battery.md
   - technologies/solid-state-battery.md
2  byd
   - companies/tesla-energy.md
   - technologies/lithium-ion-battery.md
```

Write `[[sodium-ion-battery]]` in the note where it belongs, and the missing note shows up on
this list instead of being forgotten. An unresolved link is a request, not an error, so
`links unresolved` exits 0 whatever it finds.

The full lookup order, including how ambiguous names are decided, is in
[docs/links.md](docs/links.md).

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

## Going further

- [docs/workflows.md](docs/workflows.md) - Incremental cleanup patterns, scoped migration recipes, CI gates
- [docs/links.md](docs/links.md) - Wikilink lookup order, ambiguity rules, and the unresolved-link frontier
- [docs/why.md](docs/why.md) - Background on the problem this solves


## Status

Early-stage.

## License

MIT
