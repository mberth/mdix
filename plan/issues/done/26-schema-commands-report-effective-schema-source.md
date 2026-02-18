---
id: mdix-26
title: "Schema commands should report effective schema source path"
type: task
status: done
priority: P2
parent: mdix-17
depends_on:
  - mdix-22
  - mdix-23
labels:
  - schema
  - diagnostics
  - cli
---

## Goal
Improve operator trust and reproducibility by making schema command output explicitly identify the schema file that was loaded.

## Scope
- Ensure `schema validate` and `schema migrate` output the effective schema source path when `--schema-path` is used.
- Preserve stable output shape while avoiding misleading values (currently always `mdix.schema.yml`).
- Cover both JSON and human-readable output modes.

## Acceptance criteria
- For `uv run mdix --root /Users/mberth/work/ai-barcamp-greifswald schema validate --no-strict --schema-path tests/fixtures/vault_schema_drift/mdix.schema.yml`, output includes the provided schema source path (or a clearly documented normalized equivalent).
- `schema migrate --dry-run` reports the same effective schema source behavior.
- Regression tests cover default schema discovery and explicit `--schema-path`.
