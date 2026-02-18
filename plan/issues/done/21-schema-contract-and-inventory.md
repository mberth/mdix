---
id: mdix-21
title: "Schema contract format and inventory command"
type: task
status: done
priority: P1
parent: mdix-17
depends_on: []
labels:
  - schema
  - knowledge-base
  - cli
---

## Goal
Define a vault-local schema contract (`mdix.schema.yml`) and provide a deterministic inventory command to surface frontmatter key drift.

## Scope
- Implement schema contract parsing for frontmatter fields with:
  - required/optional semantics
  - type declarations
  - enum support
- Add `mdix schema inventory` command.
- Ensure inventory output includes deterministic summary metrics and sorted field counts.

## Acceptance criteria
- Contract parsing fails with clear user-facing errors for invalid schema structure.
- `mdix schema inventory` emits deterministic JSON output.
- Inventory output includes:
  - files scanned
  - files with frontmatter
  - parse error count
  - distinct field count and per-field counts
