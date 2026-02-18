---
id: mdix-25
title: "Schema validate should scope to frontmatter notes and support path filtering"
type: task
status: done
priority: P1
parent: mdix-17
depends_on:
  - mdix-22
labels:
  - schema
  - validation
  - usability
---

## Goal
Make `mdix schema validate` usable on mixed-content vaults by avoiding noisy violations from markdown files that are not schema-managed entities.

## Scope
- Restrict required/enforced field checks to notes with parseable frontmatter by default.
- Add include/exclude path filters (for example: `--include "Personen/**"`, `--exclude "Quellen/**"`).
- Keep deterministic output ordering when filters are used.
- Ensure summary counters clearly distinguish scanned files, frontmatter files, and validated files.

## Acceptance criteria
- Running `mdix schema validate --no-strict` on `/Users/mberth/work/ai-barcamp-greifswald` no longer reports `SCHEMA_REQUIRED_MISSING` for markdown files without frontmatter (for example: `AGENTS.md`, `README.md`).
- Validation still reports real violations on schema-managed notes (for example: enum mismatches in `Personen/*` or `Organisationen/*`).
- New path filter flags can target only selected folders and produce deterministic JSON output.
