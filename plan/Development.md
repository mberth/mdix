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

### Lean thinking (flow over multitasking)
- Prefer **finishing over starting**: close the current in-progress issue before pulling a new one.
- Keep **WIP small**: default to one active child task at a time (epic tracking can stay `in_progress`).
- Choose the **smallest valuable slice** that can be implemented, tested, and documented end-to-end in one pass.
- Treat partial work as inventory: if something is blocked, either unblock quickly or pause it and move another issue to `open`.
- Prioritize **cycle time and feedback**: ship small, verify with tests, then iterate.

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
- `depends_on` (YAML list of issue ids this issue depends on; use `[]` when none)
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
depends_on: []
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
- Update status in the same session where you change code/docs/tests for that issue (do not defer status hygiene).
- Use statuses consistently:
  - `open`: not started or paused backlog work
  - `in_progress`: actively being worked this session or partially complete
  - `done`: implementation, tests, and user-facing docs/examples/acceptance criteria are all aligned
- If follow-up issues reveal acceptance-criteria or docs-contract drift for a `done` issue, move that issue back to `in_progress` until alignment is restored.
- Keep epics accurate:
  - Set epic `status: in_progress` while any child issue is `open`/`in_progress`
  - Set epic `status: done` only when all child issues are `done`, or remaining work has been explicitly moved to non-child follow-up issues
- When finishing an issue, ensure implementation is merged and pushed (per `AGENTS.md` session workflow) before marking `done`.

### Frequently used `mdix` commands for issues
In this repo, issue files live under `plan/issues/`. These commands assume you are running from the repo root.

- **Index all issues (JSON list)**
  - `uv run mdix --root plan/issues q`
- **List all issue files**
  - `uv run mdix --root plan/issues --human ls`
- **List issues that have a frontmatter key**
  - `uv run mdix --root plan/issues --human ls --has fm.parent`
  - Note: `--has fm.parent` checks key presence; `parent: null` still counts as “present”.
- **Show frontmatter for one issue**
  - `uv run mdix --root plan/issues fm show 00-sprint-1-self-manage-issues.md`
  - Get a single field: `uv run mdix --root plan/issues fm show 00-sprint-1-self-manage-issues.md | jq -r '.frontmatter.id'`
- **List open issues**
  - `uv run mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.status == "open") | .path'`
- **List all children of an epic (by parent id)**
  - `uv run mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.parent == "mdix-00") | .path'`
- **List open issues with a non-null parent**
  - `uv run mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.parent != null) | select(.frontmatter.status == "open") | .path'`
- **Search for "ready work" (open issues with no dependencies)**
  - `uv run mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.status == "open") | select((.frontmatter.depends_on // []) | length == 0) | .path'`
- **Search issues by text**
  - `uv run mdix --root plan/issues find "acceptance criteria"`

## Testing

### Tooling
- Use `pytest`.
- Prefer tests that exercise behavior end-to-end via the CLI entrypoint (i.e. running `mdix`), with a small on-disk example vault fixture.

### Linting
- Use `ruff` for linting.
- Line width is 120 characters.
- Run lint before or with tests:
  - `uv run ruff check .`

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
