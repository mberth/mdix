---
id: mdix-13
title: "Evaluate doctest-style CLI regression tests for Sprint 1 workflows"
type: task
status: open
priority: P1
parent: mdix-00
depends_on:
  - mdix-12
labels:
  - sprint-1
  - testing
  - cli
---

## Goal
Design and implement a doctest-like test approach for key Sprint 1 CLI workflows, with deterministic output checks and explicit handling of frontmatter/error edge cases.

## Scope
- Propose and validate a doctest-like harness for CLI commands and output snapshots (or equivalent golden-style assertions).
- Add/expand regression coverage for:
  - `ls` determinism and `--has fm.<field>`
  - `fm show` output schema stability, including missing and empty frontmatter
  - `find` behavior and deterministic output ordering
  - `q` output shape (`frontmatter`, `errors` presence) and stable ordering
- Keep command examples and assertions compatible with the fixture vault in `tests/fixtures/vault_great_discoveries/`.
- Document trade-offs and recommended long-term test style in a short note (test module docstring or `plan/` note).

## Acceptance criteria
- A concrete doctest-like testing pattern is documented and used by at least one test per command area (`ls`, `fm show`, `find`, `q`).
- New tests assert deterministic ordering and stable output schemas, not just presence of substrings.
- Edge cases for missing/empty frontmatter are covered in `fm show` and reflected in expected output shape.
- `uv run pytest` passes with the new regression coverage.

## Notes
- This issue is intentionally scoped to establish the pattern and baseline coverage; broader query-language tests can follow separately.
