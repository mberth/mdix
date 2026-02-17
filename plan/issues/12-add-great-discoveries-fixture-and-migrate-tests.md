---
id: mdix-12
title: "Add committed great-discoveries fixture vault and migrate tests to it"
type: task
status: open
priority: P1
parent: mdix-00
depends_on: []
labels:
  - sprint-1
  - testing
  - fixtures
---

## Goal
Create and adopt a committed fixture vault at `tests/fixtures/vault_great_discoveries/` so Sprint 1 tests run against realistic on-disk notes with deterministic assertions.

## Scope
- Add `tests/fixtures/vault_great_discoveries/` using the structure documented in `plan/Development.md`:
  - `people/`
  - `discoveries/`
  - `subjects/`
  - `media/`
- Add representative markdown notes (some with frontmatter, some without, and at least one malformed/edge-case example suitable for error-path tests).
- Update existing tests to copy the fixture vault into `tmp_path` and run CLI commands against the copied root.
- Ensure tests do not mutate committed fixture files in-place.

## Acceptance criteria
- The committed fixture directory exists at `tests/fixtures/vault_great_discoveries/` with notes in all four subdirectories.
- Tests that currently handcraft ad-hoc vault trees are migrated to the committed fixture pattern where practical.
- Test setup follows: copy fixture to temp dir, run `mdix --root <temp-copy> ...`, assert deterministic outputs.
- `uv run pytest` passes locally using the fixture-driven setup.

## Notes
- Keep fixture filenames stable, lowercase, and hyphenated to avoid platform-specific surprises.
- Keep fixture content small enough to remain readable in reviews.
