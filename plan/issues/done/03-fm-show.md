---
id: mdix-03
title: "Implement frontmatter handling"
type: task
status: done
priority: P2
parent: mdix-00
depends_on:
  - mdix-01
labels:
  - sprint-1
  - mvp
  - frontmatter
---

## Goal
Implement `mdix fm show <path>` to read YAML frontmatter from a note.

## Scope (first chunk)
- Parse optional YAML frontmatter at the top of a markdown file
- Handle files with:
  - no frontmatter
  - empty frontmatter
  - malformed YAML (surface a clear error)
- Output:
  - default JSON (frontmatter converted from yaml to JSON, sorted keys)
  - `--human`: pretty printed yaml

## Acceptance criteria
- `mdix fm show path/to/note.md` returns JSON with:
  - path (relative to root)
  - frontmatter (object or null)
  - errors (if any) in a structured form
- Deterministic key ordering in JSON output (or documented canonicalization)
- From this repo root, `mdix --root plan/issues fm show 00-sprint-1-self-manage-issues.md | jq -r '.frontmatter.id'` outputs `mdix-00`
