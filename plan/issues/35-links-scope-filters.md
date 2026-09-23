---
id: mdix-35
title: "Scope link commands with --include and --exclude"
type: task
status: in_progress
priority: P2
parent: mdix-19
depends_on:
  - mdix-34
labels:
  - cli
  - links
  - scope
---

## Goal
Give `mdix links ls` and `mdix links unresolved` the same `--include`/`--exclude` glob filters that `schema validate` and `schema migrate` have, so a vault can leave templates and other scaffolding out of its link graph.

## Why
Every vault has notes that are not content. Template notes are the common case: `_templates/source.md` holds `[[Some page]]` as a placeholder, and that placeholder shows up as the most useful-looking row in `mdix links unresolved`. Filtering it out with `jq` after the fact works but is noise in every command an agent is told to run, and it cannot filter before the scan.

## Scope
- `--include`/`--exclude` on `links ls` and `links unresolved`, repeatable, matched against paths relative to `--root`, same semantics as the schema commands.
- The filters select which notes are **scanned**. Resolution still sees the whole vault, so an excluded note is still a valid link destination.
- Help text and `docs/links.md` say which side of the link the filter applies to.

## Out of scope
- Filters on `links resolve`: it resolves one target against the vault, there is nothing to scope.
- A vault-level ignore file. `--exclude` plus a shell alias covers it for now.

## Acceptance criteria
- `mdix links unresolved --exclude "_templates/**"` drops targets that only templates link, and drops those notes from the `sources` of targets that survive.
- `mdix links ls --include "people/**"` lists only links written in `people/`.
- A note excluded from the scan still resolves as a destination for links in scanned notes.
- `--include` and `--exclude` combine the same way they do in `schema validate` (include first, then exclude).
- Both commands keep their current output shape and exit codes.
