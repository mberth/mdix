---
id: mdix-22
title: "Schema validate command and deterministic quality gate behavior"
type: task
status: done
priority: P1
parent: mdix-17
depends_on:
  - mdix-21
labels:
  - schema
  - validation
  - ci
---

## Goal
Implement deterministic schema validation output and stable non-zero exit behavior suitable for CI/local quality gates.

## Scope
- Add `mdix schema validate`.
- Validate required fields, type constraints, enum constraints, and frontmatter parse errors.
- Emit deterministic JSON diagnostics with stable rule codes and sorted ordering.
- Support strict gate behavior with deterministic exit code on violations.

## Acceptance criteria
- `mdix schema validate` outputs violations with stable machine-readable fields (code/path/field/actual/expected/message).
- Violations are deterministically ordered.
- Strict mode exits non-zero when violations exist.
- Human-readable mode provides concise per-violation lines for local operator workflows.
