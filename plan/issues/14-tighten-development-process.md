---
id: mdix-14
title: "Epic: Tighten development process"
type: epic
status: in_progress
priority: P1
parent: null
depends_on: []
labels:
  - process
  - epic
  - testing
---

## Goal
Improve development reliability and collaboration speed by making test intent more readable and regression checks more deterministic.

## Definition of done
- Process-facing decisions are documented in issue records with clear rationale.
- Narrative regression test style is standardized and documented.
- The chosen test style is implemented and enforced in CI-ready tests.
- Follow-up tickets under this epic have clear dependencies and objective acceptance criteria.

## In scope
- Decision records for test-style and workflow conventions.
- Specification and implementation of narrative Markdown CLI regression tests.
- Deterministic output assertions for key `mdix` command workflows.

## Out of scope (defer)
- New query-language features not required for the process improvements.
- Broad doc system migrations (for example, full notebook-first test tooling).

## Child issues
- `mdix-10` Bug: README CLI examples do not match implemented Sprint 1 commands
- `mdix-12` Add committed great-discoveries fixture vault and migrate tests to it
- `mdix-13` Evaluate doctest-style CLI regression tests for Sprint 1 workflows
- `mdix-15` Implement Markdown narrative CLI regression test runner
