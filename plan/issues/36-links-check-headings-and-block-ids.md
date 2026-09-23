---
id: mdix-36
title: "Check #Heading and #^block-id subpaths with --subpaths"
type: task
status: done
priority: P2
parent: mdix-19
depends_on:
  - mdix-34
labels:
  - cli
  - links
---

## Goal
Let `mdix links` tell whether the heading or block a link points at exists, so a vault can queue sections the same way it queues notes: `[[Complex I#N module]]` written before the `## N module` section exists.

## Why
`links resolve` stops at the file. `[[Complex I#N module]]` resolves to `Complex I.md` whether or not that note has the heading, so an owed section never shows up on the frontier. Obsidian behaves the same way (it opens the note), which is why the check is opt-in.

## Scope
- `--subpaths` on `links resolve`, `links ls` and `links unresolved`.
- `resolve --subpaths` adds `subpath_found` and exits 1 when the heading or block is missing.
- `ls --subpaths` adds `subpath_found` to every record; with `--unresolved-only` it also lists links whose subpath is missing.
- `unresolved --subpaths` adds one row per missing `note#subpath`, with `note` and `subpath` fields, ranked with the note rows.
- Headings are ATX headings (`#` to `######`) outside frontmatter and fenced code, compared like note names. `#A#B` needs both headings. `#^id` needs a `^id` marker at the end of a line.

## Out of scope
- Setext headings (`===`/`---` underlines).
- Obsidian's heading-link character stripping (`[[Note#a: b]]` vs a heading with other punctuation).

## Acceptance criteria
- Without `--subpaths`, every command's output and exit code is unchanged (showboat specs verify).
- `mdix links resolve "[[Note#Missing]]" --subpaths` exits 1 and reports `"subpath_found": false`.
- `mdix links unresolved --subpaths` lists `Note#Missing` with the destination note, grouped case-insensitively, counted by linking notes.
- A heading inside a code fence or a `#` comment in frontmatter does not count.
