---
id: mdix-23
title: "Schema migrate command with dry-run and safe rename transforms"
type: task
status: done
priority: P1
parent: mdix-17
depends_on:
  - mdix-21
labels:
  - schema
  - migration
  - cli
---

## Goal
Provide a safe migration flow for legacy frontmatter keys into canonical schema keys with preview-first workflows.

## Scope
- Add `mdix schema migrate` command.
- Implement `rename` migration operation based on schema contract mappings.
- Add `--dry-run` preview mode and non-dry-run apply mode.
- Ensure migration behavior avoids overwriting already-present canonical targets.

## Acceptance criteria
- Dry-run mode reports planned operations without mutating files.
- Apply mode rewrites only files that need updates.
- Migration output includes deterministic summary metrics and per-file operation details.
- Legacy-to-canonical transforms from motivating examples (`rolle`, `kontakt_email`) are supported.
