## Development guidelines

## Tech stack
- **CLI**: `click`
- **Frontmatter**: `python-frontmatter`
- **Obsidian compatibility helpers**: `obsidian-tools`
- **Dependency management**: `uv`

## Product principles

### Unix philosophy
- Prefer **small, composable** commands.
- Prefer **structured output** (JSON/JSONL) that users can **pipe into other tools** (`jq`, `rg`, `xargs`, shell).
- If a use case can be solved cleanly by piping, prefer that over adding another feature/flag.

### Principle of least surprise (agent-first)
- Favor defaults and option names a **competent AI agent** (and Unix user) would predict.
- Keep **naming consistent** across commands (`--root`, `--json`, `--human`, etc.).
- Be deterministic by default (stable ordering; stable schemas).

### Obsidian-first compatibility
- We aim to be compatible with **any Obsidian vault** out there.
- If in doubt, do what **Obsidian** does and **document the behavior**.
- Example: Obsidian allows **spaces in filenames**. `mdix` must handle them correctly (CLI usage, quoting, output).

## Writing issues (in-repo)

This repo tracks work using markdown issues under `plan/issues/`. Prefer issues that are small, testable, and written so both humans and agents can execute them with minimal back-and-forth.

### Where issues live
- **Directory**: `plan/issues/`
- **File type**: `*.md`
- **Naming**: follow the existing pattern (e.g. `01-cli-scaffold.md`, `06-issue-parent-field.md`)

### Required frontmatter (minimum schema)
Each issue starts with YAML frontmatter with at least:
- `id` (e.g. `mdix-01`)
- `title` (short, descriptive)
- `type` (usually `task` or `epic`)
- `status` (`open`, `in_progress`, `done`)
- `priority` (`P0`-`P4`)
- `parent` (epic/sprint linkage; use `null` when none)
- `labels` (YAML list)

Example (copy/paste and edit):

```yaml
---
id: mdix-XX
title: "Short, specific title"
type: task
status: open
priority: P2
parent: mdix-00
labels:
  - sprint-1
  - mvp
---
```

### Body structure (use existing issues as the template)
Use headings like the current issues do:
- **Goal**: what success means in 1-3 sentences
- **Scope**: what is in/out (bullets)
- **Acceptance criteria**: objective checks (bullets); prefer concrete CLI examples when applicable
- **Notes / Examples** (optional): extra context, demo commands, links

### Status updates
- Move work forward by updating `status:` in frontmatter.
- When finishing an issue, set `status: done` and ensure the implementation is merged and pushed (per `AGENTS.md` session workflow).

## Testing

### Tooling
- Use `pytest`.
- Prefer tests that exercise behavior end-to-end via the CLI entrypoint (i.e. running `mdix`), with a small on-disk example vault fixture.

### Running tests
- Sync the environment:
  - `uv sync`
- Run tests:
  - `uv run pytest`
- Run a single test (example):
  - `uv run pytest -k test_name`

### Preferred: end-to-end tests with an example vault
- **Goal**: Treat tests as black-box checks of `mdix` behavior over a real vault on disk.
- **Approach**:
  - Keep a committed fixture vault under `tests/fixtures/`.
  - In each test, copy the fixture vault into `tmp_path` and point `mdix` at that temp copy (never mutate the committed fixture in-place).
  - Use stable assertions (sort outputs; don’t depend on filesystem iteration order).
  - Assert on machine-friendly output (`--json` / JSON output) whenever possible.

### Example fixture vault theme: great scientific discoveries
- **Theme**: Great scientific discoveries.
- **Pages**:
  - `people/` (scientists)
  - `discoveries/` (discoveries / theories / experiments)
  - `subjects/` (fields and topics)
  - `media/` (articles, videos, talks about the above)

### Suggested fixture structure (committed)
- `tests/fixtures/vault_great_discoveries/`
  - `people/`
  - `discoveries/`
  - `subjects/`
  - `media/`

### Suggested note conventions (fixture + future real vaults)
- **Paths are identifiers**: Prefer stable, lowercase, hyphenated filenames (e.g. `people/marie-curie.md`).
- **Frontmatter is optional but encouraged** for tests that cover metadata features.
- **Use simple, consistent fields** in the fixture:
  - `title`: human title
  - `type`: one of `person`, `discovery`, `subject`, `media`
  - `tags`: list of strings (optional)
  - `status`: e.g. `active` / `draft` (optional)

### Minimal example note (illustrative)
```yaml
---
title: "Marie Curie"
type: person
tags: ["physics", "chemistry"]
---
```

### What an end-to-end test should look like (high level)
- Arrange: copy `tests/fixtures/vault_great_discoveries` to a temp dir
- Act: run `uv run mdix --root <temp-vault> <command> ...`
- Assert: verify deterministic output and key fields/content
