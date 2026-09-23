---
id: mdix-34
title: "Wikilink resolution and an unresolved-link frontier command"
type: task
status: in_progress
priority: P1
parent: mdix-19
depends_on: []
labels:
  - cli
  - links
  - graph
  - obsidian
---

## Goal
Give `mdix` a first-class view of the wikilink graph: resolve a single `[[wikilink]]` the way Obsidian resolves it (from a given page), list every link in the vault with its resolution status, and list the links that resolve to no note yet. The last one is the interesting list: in a growing vault, unresolved links are the pages you have not written, ranked by how often you referred to them.

## Why
Vaults that are maintained by a human and an agent together grow outward from what is already written. You finish a note, link the entities it mentions, and the links that point nowhere become the queue for the next note. Obsidian shows those as unresolved links in the graph view; there is no way to get them on the command line, with counts and source pages, in a form an agent can sort and pick from.

Resolution has to match Obsidian, or the counts are wrong: a link is a name, not a path, and Obsidian resolves it against the vault with a documented set of fallbacks.

## Scope
- New module `src/mdix/links.py`: scan markdown for wikilinks, resolve a link target against the vault.
- New command group `mdix links`:
  - `mdix links resolve TARGET [--from PATH]` - resolve one wikilink and report the destination and how it was found. Accepts `Foo`, `[[Foo]]`, `Foo#Section|alias`, `../other/Foo`.
  - `mdix links ls [--from PATH] [--unresolved-only]` - every wikilink occurrence with its resolution status.
  - `mdix links unresolved` - the frontier: one row per unresolved target, with the number of notes that link it and the notes they are, sorted by count descending, then target.
- Resolution rules follow Obsidian ("shortest path when possible"), documented in `docs/links.md`:
  - split off `#subpath` and `|display` before resolving
  - exact vault-relative path, then a path relative to the source note (`./`, `../`)
  - otherwise match by basename anywhere in the vault, preferring the same folder as the source note, then the shallowest path, then lexicographic order
  - append `.md` when the target has no extension
  - case-insensitive filename matching
  - frontmatter `aliases` as the last fallback
- Scanning fidelity: links inside fenced code blocks and inline code do not count (Obsidian does not link them); links in frontmatter values do count (Obsidian shows them as links); embeds `![[...]]` count and are flagged.
- Documentation: `docs/links.md` for the lookup logic and the frontier workflow, README command table and a short section.
- Tests: a committed fixture vault covering ambiguity, relative paths, aliases, subpaths, code blocks, and unresolved targets; showboat spec for the three commands.

## Out of scope
- Rewriting or creating links (`links add`, auto-linking prose).
- Markdown-style links `[text](note.md)` - wikilinks only for now.
- Checking that a `#heading` or `#^block` subpath exists in the destination note.
- A CI gate that fails on unresolved links. An unresolved link is a request, not an error; pipe to `jq length` if you want a threshold.

## Acceptance criteria
- `mdix links resolve Tesla` prints the resolved path, the rule that matched, and exits 0; it exits 1 when nothing matches.
- `mdix links resolve "[[Foo|bar]]" --from companies/catl.md` strips the display text and resolves relative to `companies/catl.md`.
- `mdix links ls` returns one record per occurrence with `path`, `line`, `target`, `subpath`, `display`, `embed`, `resolved`, `via`, in deterministic order.
- `mdix links unresolved` returns `target`, `count`, `sources` per unresolved target, sorted by `count` descending then `target`; `count` counts notes, not occurrences.
- A link written inside a fenced code block or inline code appears in no output.
- A link in a frontmatter value resolves like a link in prose.
- Two notes with the same basename resolve to the one in the source note's folder.
- `--human` output is supported for all three commands; default stays JSON.
- `docs/links.md` documents the lookup order with a worked example per rule.

## Notes / Examples
```bash
# what should I write next?
mdix --root ~/notes links unresolved --human

# where does this link go from here?
mdix --root ~/notes links resolve "[[Fluence]]" --from projects/moss-landing.md

# every unresolved occurrence, as JSON
mdix --root ~/notes links ls --unresolved-only | jq -r '.[] | "\(.path):\(.line) \(.target)"'
```
