---
id: mdix-20
title: "Epic: Outreach prioritization and operations cockpit"
type: epic
status: open
priority: P1
parent: null
depends_on:
  - mdix-17
  - mdix-18
labels:
  - epic
  - knowledge-base
  - operations
---

## Goal
Provide generalized `mdix` pipeline and prioritization features so any action-oriented vault can turn notes into an executable operations queue.

## Why this epic exists
Many research/operations vaults already contain priorities and next-step intent, but that logic is often fragmented and non-deterministic. `mdix` should provide native pipeline mechanics.

Motivating examples from sampled vault (`tmp/ai-barcamp-greifswald/`):
- Prioritization logic is spread across multiple docs (tiers, status notes, contact lists).
- Next actions are mostly free text and hard to turn into a deterministic queue.
- Progress metrics are manually maintained in status documents.

## Impact
- **Product impact:** Very high. Positions `mdix` as an execution layer, not just an index/query CLI.
- **Execution impact:** Very high. Produces clear "what to do next" queues.
- **Planning impact:** High. Enables campaign-level visibility and pacing.

## Scope
- Define a generic pipeline model for vault records (states, owner, next_action, due_date, last_touched_at, outcome).
- Build ranking/query commands that combine priority, relevance, confidence, and freshness.
- Generate tactical outputs: daily queue, weekly pipeline report, and coverage/gap analysis.
- Add lightweight workflow support to update outcomes and state transitions.

## Out of scope
- Full CRM replacement.
- Fully autonomous outbound actions without operator review.

## Acceptance criteria
- `mdix` supports structured pipeline state for vault entities, not only prose markers.
- `mdix` can produce deterministic top-N prioritized queues with rationale fields.
- `mdix` can emit funnel metrics (for example: identified -> verified -> contacted -> confirmed).
- Users can update outcomes/state in a repeatable CLI workflow.
- Reference runbooks demonstrate end-to-end usage on a fixture vault.

## Implementation plan
- **Phase 1 - Pipeline model**
  - Define lifecycle fields and allowed transitions.
  - Map common vault patterns (tiers, statuses, checklists) into model fields.
- **Phase 2 - Prioritization engine**
  - Implement weighted ranking with transparent scoring factors.
  - Add `next_action` queue generation and due-date ordering.
- **Phase 3 - Reporting**
  - Add funnel and coverage reports by configurable dimensions.
  - Add blocked/stale slices for operational triage.
- **Phase 4 - Operationalization**
  - Add runbooks for daily/weekly usage.
  - Add regression fixtures to ensure deterministic queue/report outputs.

## Notes
- This epic converts research depth into predictable outreach throughput.
