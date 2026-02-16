---
id: mdix-05
title: "Implement mdix ls --has fm.FIELD frontmatter presence filter"
type: task
status: open
priority: P2
parent: mdix-00
labels:
  - sprint-1
  - mvp
  - frontmatter
---

## Goal
Implement `mdix ls` with `--has fm.<field>` as shown in README.

## Scope (first chunk)
- Command: `mdix ls --has fm.tags` (example)
- Interpret `fm.<field>` as “frontmatter contains this top-level key”
- Output:
  - default JSON list of note paths (stable ordering)
  - `--human`: one path per line

## Acceptance criteria
- `mdix ls --has fm.tags` returns only notes that contain `tags:` in frontmatter
- Handles missing / malformed frontmatter gracefully (errors are surfaced consistently)
- From this repo root, `mdix --root plan/issues ls --has fm.parent` returns JSON containing at least `plan/issues/00-sprint-1-self-manage-issues.md`
