---
id: mdix-30
title: "Expand schema migrate with path scoping and non-rename operations"
type: task
status: done
priority: P2
parent: null
depends_on:
  - mdix-23
labels:
  - schema
  - migrate
  - usability
---

## Goal
Make `mdix schema migrate` practical for incremental vault cleanup by matching `schema validate` scoping and supporting common non-rename transforms.

## Scope
- Add repeatable `--include` and `--exclude` path filters to `schema migrate`.
- Extend migration operations beyond `rename` for common schema-hardening steps:
  - value mapping (`value_map`) for enum normalization
  - optional null-key removal (`unset_if_null`)
  - default assignment when missing (`set_default`)
- Preserve deterministic change ordering and stable JSON output.
- Keep dry-run preview semantics clear and backward-compatible.

## Acceptance criteria
- `schema migrate` can target a subset of the vault using include/exclude patterns.
- At least one non-rename migration operation can be executed from `mdix.schema.yml` with dry-run preview and apply parity.
- Regression tests cover scoped migrations and new operation behavior on fixture vaults.
