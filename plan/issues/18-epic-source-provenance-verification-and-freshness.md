---
id: mdix-18
title: "Epic: Source provenance, verification, and freshness lifecycle"
type: epic
status: open
priority: P1
parent: null
depends_on:
  - mdix-17
labels:
  - epic
  - knowledge-base
  - provenance
---

## Goal
Add generalized `mdix` provenance and freshness features so any vault can track fact confidence and verification lifecycle in structured form.

## Why this epic exists
Knowledge vaults often store evidence, but verification state tends to be prose-only. `mdix` should make provenance queryable and enforceable.

Motivating examples from sampled vault (`tmp/ai-barcamp-greifswald/`):
- Contact entries often include guessed emails and free-text verification notes.
- Notes distinguish direct vs indirect verification, but not as structured fields.
- Reports age quickly and do not consistently expose "last verified" metadata.

Without structured provenance, users cannot reliably answer: "Which high-priority records are currently verified?"

## Impact
- **Product impact:** High. Positions `mdix` as a trustworthy evidence-aware vault tool.
- **Operational impact:** High. Focuses teams on actionable, verified records.
- **Maintenance impact:** Medium-high. Enables freshness checks instead of repeated manual audits.

## Scope
- Add a canonical provenance model for fact-bearing fields (source URL, evidence type, verification method, verified_at, confidence).
- Add validation rules for verification states and freshness windows.
- Implement query/report commands for stale or weakly verified records.
- Add workflow helpers to promote records from guessed to verified with audit trail.

## Out of scope
- Automated crawling behind authentication walls.
- Fully autonomous verification without human review.

## Acceptance criteria
- `mdix` exposes a documented provenance model that vaults can adopt.
- `mdix` can filter/query records by confidence, verification_state, and verification age.
- `mdix` can generate stale-record reports with deterministic ordering.
- Workflow commands/checks support guessed -> verified transitions with source attribution.
- Regression fixtures include motivating examples from sampled vault patterns.

## Implementation plan
- **Phase 1 - Provenance model**
  - Define provenance fields, enums, and confidence scale.
  - Specify vault-configurable freshness policies.
- **Phase 2 - Query primitives**
  - Add filters for confidence, verification_state, and verified_at freshness.
  - Add machine-friendly stale-record report output.
- **Phase 3 - Workflow support**
  - Add command paths to record verification actions with source references.
  - Provide templates/checklists for standard verification updates.
- **Phase 4 - Governance**
  - Add defaults for expiration windows by field class.
  - Add docs for periodic re-verification workflow.

## Notes
- This epic compounds value from schema normalization and unlocks high-signal outreach queues.
