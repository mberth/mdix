---
id: mdix-09
title: "Defer: add mdix q --where expression filtering"
type: task
status: open
priority: P3
parent: null
depends_on: []
labels:
  - backlog
  - query
---

## Goal
Add a `--where` filter language to `mdix q` so filtering can happen inside `mdix` (instead of in `jq`).

## Why deferred
Sprint 1 can manage in-repo issues by emitting structured JSON and filtering with `jq`.

## Scope (later)
- `mdix q --where '<expr>'` support
- Document supported subset
- Stable errors on invalid expressions

## Examples (later)
- `mdix --root plan/issues q --where 'parent == "mdix-00"'`
- `mdix --root plan/issues q --where 'status == "open" and labels.contains("sprint-1")'`

