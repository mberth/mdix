---
id: mdix-19
title: "Epic: Entity resolution and link integrity for people, orgs, and themes"
type: epic
status: in_progress
priority: P2
parent: null
depends_on:
  - mdix-17
labels:
  - epic
  - knowledge-base
  - graph
---

## Goal
Build `mdix` entity-resolution and link-integrity capabilities that help any vault maintain a coherent note graph as it scales.

## Why this epic exists
Most vaults rely on naming conventions and human discipline for entity identity. `mdix` should provide explicit graph hygiene tools so identity remains stable over time.

Motivating examples from sampled vault (`tmp/ai-barcamp-greifswald/`):
- References point to mixed naming forms and aliases across folders and reports.
- Contact summaries, source reports, and canonical entity notes can diverge.
- Duplicate entity candidates are hard to spot early in growth.

## Impact
- **Product impact:** High. Expands `mdix` from file tooling to graph maintenance tooling.
- **Data integrity impact:** High. Reduces duplicates and unresolved references.
- **Analytics impact:** Medium-high. Improves counts, rankings, and cross-note joins.

## Scope
- Define a vault-level entity identity contract (`canonical_name`, `slug`, `aliases`, optional external IDs).
- Implement duplicate-candidate detection for person/org-style entities.
- Implement unresolved-link and broken-target checks for wikilinks.
- Add merge guidance/workflow that preserves provenance and alias redirects.

## Out of scope
- Full semantic dedup with external identity providers.
- Aggressive auto-merging without review.

## Acceptance criteria
- `mdix` documents and supports canonical identity fields for entity notes.
- `mdix` can report likely duplicates with deterministic confidence hints.
- `mdix` can list unresolved/broken wikilinks with file/target context.
- A safe merge workflow exists that preserves provenance and alias history.
- Regression fixtures cover alias drift and duplicate patterns from motivating examples.

## Implementation plan
- **Phase 1 - Identity model**
  - Define identity fields and collision rules.
  - Add inventory command for alias and slug coverage.
- **Phase 2 - Detection**
  - Add fuzzy/entity heuristics for duplicate candidate surfacing.
  - Add unresolved-link checks in machine-readable output.
- **Phase 3 - Resolution workflow**
  - Add guided merge flow with dry-run and explicit conflict reporting.
  - Preserve alias history to avoid future broken references.
- **Phase 4 - Continuous checks**
  - Add regular duplicate/link hygiene checks and trend reporting.
  - Add docs for periodic graph cleanup workflows.

## Notes
- Good entity hygiene is foundational for strategic outreach and recommendation tooling.
