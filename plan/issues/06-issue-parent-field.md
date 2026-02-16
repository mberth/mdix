---
id: mdix-06
title: "Add parent field to issue frontmatter schema"
type: task
status: done
priority: P1
parent: mdix-00
labels:
  - sprint-1
  - meta
---

## Goal
Add `parent` to the issue frontmatter schema so epics/sprints can be modeled explicitly.

## Scope
- Update existing issues to include a `parent` field in frontmatter
- Update any issue templates/generators in-repo to emit `parent`
- Update docs describing the minimum issue schema

## Acceptance criteria
- All `plan/issues/*.md` have a `parent:` key in YAML frontmatter (use `null` when there is no parent)
- `AGENTS.md` documents `parent` as part of the minimum schema


