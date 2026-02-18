---
id: mdix-28
title: "q should JSON-serialize YAML date and datetime frontmatter values"
type: task
status: done
priority: P1
parent: null
depends_on: []
labels:
  - bug
  - q
  - frontmatter
---

## Goal
Make `mdix q` robust on real-world vaults where YAML frontmatter includes `date`/`datetime` scalar types.

## Scope
- Reproduce the current crash path where `mdix q` fails with `TypeError: Object of type date is not JSON serializable`.
- Ensure machine output remains valid JSON without dropping affected frontmatter fields.
- Define and document canonical conversion behavior (for example ISO-8601 strings) for non-JSON-native scalar values.
- Add regression tests using an on-disk fixture note containing date-like frontmatter.

## Acceptance criteria
- `mdix q` no longer crashes on notes containing YAML `date` or `datetime` values.
- JSON output remains deterministic and parseable by `jq`.
- Conversion semantics are documented in README/help text and covered by tests.
