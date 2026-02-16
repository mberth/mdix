---
id: mdix-02
title: "Implement find text search"
type: task
status: open
priority: P2
parent: mdix-00
labels:
  - sprint-1
  - mvp
  - find
---

## Goal
Implement `mdix find` for quick text search across a vault.

## Scope (first chunk)
- Command: `mdix find <query>`
- Search `*.md` under root recursively (skip common junk dirs like `.git`, `.venv`, `node_modules`)
- Deterministic ordering of results
- Output:
  - default: JSON (per README: machine-friendly default)
  - `--human`: readable lines

## Acceptance criteria
- `mdix find "needle"` returns matches with:
  - file path (relative to root)
  - line number (if applicable)
  - matched line snippet (or context, if supported)
- From this repo root, `mdix --root plan/issues find "Sprint goal"` returns at least one match.
- Exit codes are stable:
  - 0 when matches found
  - non-zero when no matches found (define and document which)
  - non-zero on errors

## Implementation notes
Use a standalone implementation - just python.
