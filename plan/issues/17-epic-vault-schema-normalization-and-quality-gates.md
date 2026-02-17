---
id: mdix-17
title: "Epic: Vault schema normalization and quality gates"
type: epic
status: done
priority: P1
parent: null
depends_on: []
labels:
  - epic
  - knowledge-base
  - data-quality
---

## Goal
Ship `mdix` capabilities that let any markdown vault define, validate, and evolve note schemas with low operational friction.

## Why this epic exists
Many vaults start useful but drift structurally over time. `mdix` should provide first-class schema hygiene so users do not need custom one-off scripts per vault.

Motivating examples from sampled vault (`tmp/ai-barcamp-greifswald/`):
- Person notes mix flat and nested contact models (`kontakt_email` vs `kontakt.email`).
- Role fields vary (`rolle` vs `position`), and some records omit explicit `type`.
- Status values are meaningful but inconsistent across note families (`identifiziert`, `lead`, `zu_kontaktieren`).

## Impact
- **Product impact:** High. Establishes `mdix` as a reusable data-quality layer for markdown vaults.
- **User impact:** High. Reduces manual cleanup and query fragility in medium/large vaults.
- **Risk reduction:** High. Prevents silent misses when filtering on non-canonical fields.

## Scope
- Add a vault-local schema contract format (`mdix.schema.yml` or equivalent).
- Implement `mdix schema validate` with deterministic JSON diagnostics.
- Implement `mdix schema migrate` to map legacy keys into canonical keys.
- Add summary metrics and non-zero exit behavior for quality gates.

## Out of scope
- Full content rewriting of prose sections.
- Any speculative enrichment that is not traceable to a source.

## Acceptance criteria
- `mdix` supports a documented schema contract with required/optional fields and enums.
- `mdix schema validate` reports violations in deterministic JSON and human-readable output.
- `mdix schema migrate --dry-run` previews changes; non-dry-run applies safe transforms.
- Validation can be used as a CI/local gate via deterministic exit codes.
- Sampled schema variants from the motivating vault migrate with no data loss.

## Implementation plan
- **Phase 1 - Contract and inventory**
  - Specify schema syntax and type model for frontmatter fields.
  - Add inventory command to surface key cardinality and schema drift.
- **Phase 2 - Validator**
  - Implement validation engine with stable rule codes and paths.
  - Add `--json` and `--human` output modes.
- **Phase 3 - Migrator**
  - Implement field mapping transforms (for example: `rolle -> position`, nested/flat contact normalization).
  - Support dry-run preview and reversible patch output.
- **Phase 4 - Quality gates**
  - Document pre-commit/CI usage patterns.
  - Add regression fixtures covering drift patterns from the motivating vault.

## Notes
- This epic is a prerequisite for robust ranking, dedup, and outreach automation.
- Delivered via child tasks:
  - `mdix-21` schema contract and inventory
  - `mdix-22` validator and quality gate behavior
  - `mdix-23` migrator with dry-run/apply
  - `mdix-24` fixtures, docs, and regression coverage
