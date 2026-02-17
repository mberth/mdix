---
id: mdix-29
title: "Add frontmatter batch normalize command for recurring cleanup operations"
type: task
status: done
priority: P1
parent: null
depends_on: []
labels:
  - feature
  - frontmatter
  - cleanup
---

## Goal
Replace ad-hoc one-off Python cleanup scripts with a first-class `mdix` command for deterministic frontmatter normalization at vault scale.

## Scope
- Introduce a batch normalization command (name TBD, for example `mdix fm normalize`) with `--dry-run` and apply modes.
- Support recurring operations observed in Epic 17 style cleanup:
  - map field values (for example status aliases to schema enums)
  - set default values for missing required fields
  - derive one field from another field or filename fallback
  - remove keys with null values
- Emit structured per-file change previews and summary counters.
- Keep behavior deterministic and composable for CI or scripted usage.

## Acceptance criteria
- Users can run normalization in dry-run mode and inspect file-level changes before apply.
- A single command can replace the common status/title/type/null-cleanup script pattern used in vault maintenance.
- Output is deterministic JSON by default and suitable for commit-scoped cleanup workflows.
