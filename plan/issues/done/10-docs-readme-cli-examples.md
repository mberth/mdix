---
id: mdix-10
title: "Bug: README CLI examples don’t match implemented Sprint 1 commands"
type: task
status: done
priority: P1
parent: mdix-14
depends_on: []
labels:
  - sprint-1
  - docs
  - bug
  - cli
---

## Goal
Make the README examples accurately reflect the currently implemented Sprint 1 CLI, so users can copy/paste commands successfully.

## Scope
- Update README examples for `q`, `fm`, and output shape to match the implementation in `src/mdix/cli.py`
- Remove or defer examples that imply unimplemented features (positional query expressions, `--where`, `--text`, `--json`)
- Keep examples consistent with Sprint 1’s “JSON by default” behavior and `q` output as a JSON list

## Acceptance criteria
- `README.md` does not show `mdix q 'tags.contains("ml")'` (since `q` currently takes no positional expression)
- `README.md` does not show `mdix q --where ...` or `mdix q --text ...` (explicitly deferred)
- `README.md` shows frontmatter usage as `mdix fm show path/to/note.md` (not `mdix fm path/to/note.md`)
- Any `jq` example that consumes `mdix q` assumes a JSON list (uses `.[]`, not `.results`)
- Any mention of `--json` is removed or replaced with the current reality (JSON is the default; there is no `--json` flag)

## Notes
- Concrete repro (current behavior):
  - `uv run mdix q 'tags.contains("ml")'` fails with “Got unexpected extra argument”
  - `uv run mdix --root plan/issues q` outputs a JSON list (not an object with `.results`)

