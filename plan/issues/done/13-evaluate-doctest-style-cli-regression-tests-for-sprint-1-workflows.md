---
id: mdix-13
title: "Evaluate doctest-style CLI regression tests for Sprint 1 workflows"
type: task
status: done
priority: P1
parent: mdix-14
depends_on: []
labels:
  - process
  - testing
  - cli
---

## Goal
Evaluate and choose a doctest-like approach for key CLI workflows that preserves narrative readability while enabling deterministic automated output checks.

## Scope
- Compare candidate approaches for narrative CLI regression specs:
  - BDD tools (`behave`)
  - framework-native options (`click` test helpers)
  - notebook/doc formats (Jupyter/Quarto)
  - custom Markdown-driven runner
- Capture the selected approach and rationale.
- Define canonical Markdown block conventions for command input and expected outputs.
- Spin implementation work into a dedicated follow-up task.

## Acceptance criteria
- Decision record exists in this issue with clear recommendation and trade-offs.
- The selected Markdown conventions are documented exactly as:
  - command input blocks use fenced code with language `bash`
  - expected stdout blocks use fenced code with language `expected`
  - expected stderr blocks use fenced code with language `expected-err` and default to empty if omitted
- A dedicated implementation issue exists with concrete scope and acceptance criteria.

## Notes
- Decision: use Markdown specifications plus a small custom pytest runner.
- Rationale: this keeps tests readable (narrative text, headings, examples) while preserving deterministic machine-checked assertions in CI.
- Chosen block format:
  - Input command:
    ```bash
    mdix --root tests/fixtures/vault_great_discoveries ls
    ```
  - Expected stdout:
    ```expected
    discoveries/general-relativity.md
    people/marie-curie.md
    ```
  - Expected stderr (optional, defaults to empty when not present):
    ```expected-err
    warning: example stderr line
    ```
- Follow-up implementation ticket: `mdix-15`.
