---
id: mdix-24
title: "Schema drift fixtures, docs, and markdown regression specs"
type: task
status: done
priority: P1
parent: mdix-17
depends_on:
  - mdix-22
  - mdix-23
labels:
  - schema
  - testing
  - docs
---

## Goal
Demonstrate and lock schema workflows end-to-end with committed fixtures, docs, and markdown narrative regression tests.

## Scope
- Add a schema drift fixture vault with:
  - legacy and canonical field variants
  - enum drift and missing required field examples
  - `mdix.schema.yml` contract
- Add pytest coverage for schema inventory/validate/migrate.
- Extend markdown narrative specs (`tests/specs/`) and tutorial coverage for schema commands.
- Update README command examples and schema contract documentation.

## Acceptance criteria
- `uv run pytest` passes with schema CLI tests and updated markdown regression specs.
- Tutorial docs include runnable schema examples with deterministic expected outputs.
- Regression harness supports schema fixture execution context.
