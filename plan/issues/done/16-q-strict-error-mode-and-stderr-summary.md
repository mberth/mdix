---
id: mdix-16
title: "Add strict q mode for frontmatter parse errors with stderr summary"
type: task
status: done
priority: P2
parent: null
depends_on: []
labels:
  - cli
  - q
  - error-handling
---

## Goal
Preserve `mdix q` as machine-friendly JSON output on stdout while offering an opt-in strict mode that fails when note-level parse errors are present.

## Scope
- Keep current default behavior unchanged:
  - `mdix q` emits a JSON list to stdout
  - per-note parse issues remain in each item's `errors` field
- Add a strict option (for example `--fail-on-errors` or `--strict`) to `mdix q`
- In strict mode:
  - continue emitting the full JSON payload to stdout
  - emit an error summary to stderr (count + paths and/or error types)
  - return non-zero when any item has non-empty `errors`
- Update docs/examples to explain default vs strict behavior and pipeline implications

## Acceptance criteria
- Running `mdix q` on a vault with malformed frontmatter keeps returning exit code 0 and structured per-item `errors` in stdout JSON.
- Running `mdix q --fail-on-errors` (or chosen flag) on the same vault:
  - prints machine-readable JSON payload to stdout
  - prints a concise summary to stderr
  - exits non-zero
- Running strict mode on a clean vault exits 0 and writes no stderr output.
- Tests cover both modes and assert stdout/stderr separation plus exit codes.
- README and/or development docs describe when to use default mode vs strict mode.

## Notes
- Rationale: `q` is an index/data command, so note-level parse issues belong in the data model by default; strict mode supports CI gating without breaking existing JSON pipelines.
