---
id: mdix-27
title: "Fix motivating vault pointer under tmp for reproducible epic 17 validation"
type: task
status: done
priority: P2
parent: mdix-17
depends_on: []
labels:
  - schema
  - fixtures
  - docs
---

## Goal
Keep epic 17 validation reproducible by ensuring the motivating vault path under `tmp/` resolves correctly.

## Scope
- Fix the repository-local pointer at `tmp/ai-barcamp-greifswald` so it resolves to the intended vault location.
- Document expected setup for local runs when the motivating vault lives outside the repo.
- Add a lightweight check (script/doc step) that fails fast with a clear message when the pointer is broken.

## Acceptance criteria
- `tmp/ai-barcamp-greifswald` resolves to an existing directory on a fresh local setup that follows docs.
- The epic 17 validation commands can be run against the documented `tmp/` path without manual path hunting.
- Documentation explains whether the pointer is optional, how to create/update it, and safe read-only usage for test runs.
