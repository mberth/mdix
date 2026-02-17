---
id: mdix-15
title: "Implement Markdown narrative CLI regression runner"
type: task
status: open
priority: P1
parent: mdix-14
depends_on:
  - mdix-12
  - mdix-13
labels:
  - process
  - testing
  - cli
---

## Goal
Implement a minimal Markdown-driven regression harness for `mdix` CLI workflows so tests can be both human-readable and machine-verified.

## Scope
- Implement a pytest helper/runner that reads Markdown spec files and executes each `bash` command block.
- Parse and validate the expected output blocks:
  - `expected` for stdout
  - `expected-err` for stderr (default expected stderr is empty when omitted)
- Fail tests with clear diffs when actual output does not match expectations.
- Add initial narrative spec documents and wire them into `uv run pytest`:
  - `ls` determinism and `--has fm.<field>`
  - `fm show` output shape, including missing/empty frontmatter behavior
  - `find` deterministic ordering
  - `q` stable output shape (`frontmatter`, `errors`) and ordering
- Keep examples compatible with `tests/fixtures/vault_great_discoveries/`.

## Acceptance criteria
- At least one Markdown narrative regression spec exists for each command area: `ls`, `fm show`, `find`, `q`.
- Spec format is implemented exactly:
  - input commands in fenced `bash` blocks
  - expected stdout in fenced `expected` blocks
  - expected stderr in fenced `expected-err` blocks
  - omitted `expected-err` means stderr must be empty
- Test failures show actionable output diffs for stdout/stderr mismatches.
- `uv run pytest` passes with the new harness and coverage.

## Notes
- Keep the runner intentionally small and explicit; avoid creating a large custom DSL.
- Prefer deterministic outputs and stable JSON assertions over substring-only checks.
