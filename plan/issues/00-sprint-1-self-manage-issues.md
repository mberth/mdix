---
id: mdix-00
title: "Epic: Sprint 1 — mdix can manage its own issues"
type: epic
status: open
priority: P0
parent: null
labels:
  - sprint-1
  - epic
  - mvp
---

## Sprint goal
Make `mdix` marginally useful for managing the repo's own issues in `plan/issues/`.

## Definition of done
- From the repo root, `mdix` can list issue markdown files deterministically.
- `mdix` can show parsed issue frontmatter (YAML) as stable JSON.
- `mdix` can text-search issues under `plan/issues/`.
- `mdix` can list an epic's child issues via `parent == "<epic id>"`.
- The issue schema supports an explicit `parent` field so a sprint/epic can be modeled in frontmatter.
- `mdix` can emit enough structured JSON for `jq` to do filtering by frontmatter fields (e.g. `parent`, `status`, `labels`) without re-reading files.

## In scope
- CLI scaffold and root handling (`--root` / `MDIX_ROOT`)
- `mdix ls` (deterministic enumeration)
- `mdix ls --has fm.<field>` (frontmatter presence filter)
- `mdix fm show` (parse + display frontmatter)
- `mdix find` (text search)
- `mdix q` (minimal query slice sufficient for issues)
- Issue schema update: add `parent` to frontmatter and adopt it in existing issues

## Out of scope (defer)
- Mutating notes/issues (`fm set|unset`) beyond stubbed help
- Creating new notes/issues (`mdix new`) beyond stubbed help
- Query language / expression parsing in `mdix q` (e.g. `--where`)
- Rich query language beyond the documented minimal subset (e.g. `or`, numeric comparisons, nested field access)
- Batch edit workflows

## Examples / Demo

List this epic's child issues:

```bash
mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.parent == "mdix-00") | .path'
```

List all open issues:

```bash
mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.status == "open") | .path'
```

List all open Sprint 1 issues (epic + children):

```bash
mdix --root plan/issues q | jq -r '.[] | select((.frontmatter.labels // []) | index("sprint-1")) | select(.frontmatter.status == "open") | .path'
```

Count open issues:

```bash
mdix --root plan/issues q | jq '[.[] | select(.frontmatter.status == "open")] | length'
```

Print open issue paths:

```bash
mdix --root plan/issues q | jq -r '.[] | select(.frontmatter.status == "open") | .path'
```

