# Wikilinks: how mdix resolves them

`mdix links` reads `[[wikilinks]]` the way Obsidian does, so the numbers it reports match
what you see in Obsidian's graph. This page is the contract: what counts as a link, how a
link target becomes a file, and what happens when it does not.

The commands:

```bash
mdix links resolve TARGET [--from PATH]   # where does this link go?
mdix links ls [--from PATH]               # every link, with its destination
mdix links unresolved                     # every target with no note behind it
```

## The shape of a link

```
![[folder/note#Heading|display text]]
 ^  ^           ^        ^
 |  target      subpath  display
 embed
```

- Everything after the first `|` is **display text**. It never affects resolution.
- Everything from the first `#` of the path part is the **subpath**: `#Heading`, or `#^block-id`
  for a block reference. By default it is reported but not verified: `mdix` resolves to the file,
  as Obsidian does. Pass `--subpaths` to check it (see [Headings and blocks](#headings-and-blocks)).
- A leading `!` makes it an **embed**. Embeds resolve exactly like links and are flagged with
  `"embed": true`.
- A link with only a subpath, `[[#Heading]]`, points at the note it is written in.

## What counts as a link

`mdix` scans a note the way Obsidian renders it:

| Where | Counted | Why |
|---|---|---|
| Prose, lists, tables, callouts | yes | ordinary links |
| Frontmatter values (`home: "[[index]]"`) | yes | Obsidian renders property links and counts them in the graph |
| Fenced code blocks (``` ``` ```, `~~~`) | no | Obsidian does not link code |
| Inline code (`` `[[example]]` ``) | no | same |

Three known gaps, all deliberate for now:

- Markdown-style links, `[text](note.md)`, are not scanned. Wikilinks only.
- Indented code blocks (four spaces, no fence) are scanned. Fencing them is the fix; nested list
  items are far more common than indented code, and dropping them would lose real links.
- Inline code is detected per line, so a code span that wraps across two lines is only masked on
  the line where it opens.

## The lookup order

A link target is a **name**, not a path. `mdix` tries these rules in order and stops at the first
one that matches a file. `--from PATH` is the note the link is written in; without it, rules that
depend on the source note are skipped.

Each rule below is shown against this vault:

```
index.md
people/ada-lovelace.md          (aliases: Ada, Countess of Lovelace)
people/overview.md
projects/analytical-engine.md
projects/overview.md
projects/hardware/mill.md
attachments/diagram.png
```

**1. Empty target - the note itself** (`via: "self"`)

`[[#Notes]]` from `projects/analytical-engine.md` resolves to `projects/analytical-engine.md`.

**2. Explicit relative path** (`via: "relative_path"`)

A target starting with `./` or `../` is resolved against the source note's folder:
`[[../projects/analytical-engine]]` from `people/ada-lovelace.md` -> `projects/analytical-engine.md`.
A path that climbs out of the vault resolves to nothing.

**3. Vault-root path** (`via: "exact_path"`)

`[[people/ada-lovelace]]` -> `people/ada-lovelace.md`, from anywhere.

**4. Path relative to the source note** (`via: "relative_path"`)

A target with a `/` that did not match at the root is tried under the source note's folder:
`[[hardware/mill]]` from `projects/analytical-engine.md` -> `projects/hardware/mill.md`.

**5. Partial path anywhere in the vault** (`via: "path_suffix"`)

A target with a `/` that still did not match is matched against the *end* of every path:
`[[hardware/mill]]` from `index.md` -> `projects/hardware/mill.md`.

**6. Name anywhere in the vault** (`via: "basename"`)

A target without a `/` matches any file whose name (without the `.md`) is that name:
`[[ada-lovelace]]` -> `people/ada-lovelace.md`. This is the common case, and the one Obsidian's
"shortest path when possible" setting produces.

**7. Frontmatter alias** (`via: "alias"`)

If nothing matched by name, notes are searched by their `aliases` (or the older singular `alias`)
frontmatter field: `[[Countess of Lovelace]]` -> `people/ada-lovelace.md`. Pass `--no-aliases` to
turn this rule off.

If no rule matches, the link is unresolved: `resolved` is `null`, `via` is `null`, and
`links resolve` exits 1.

## Matching details

- **Extensions.** A target without an extension gets `.md` appended. A target with one is matched
  as written, so `[[diagram.png]]` finds the attachment.
- **Attachments.** Every file in the vault is a resolution candidate, not only `.md` files.
- **Case.** Names match case-insensitively: `[[ADA-LOVELACE]]` finds `people/ada-lovelace.md`.
- **Unicode.** Targets and filenames are compared after NFC normalization, so a precomposed `é`
  and a decomposed `e` + combining accent are the same name.
- **Whitespace.** Runs of whitespace collapse to one space, and the target is trimmed.
- **Ignored folders.** The vault walk skips `.git`, `.venv`, `node_modules`, `__pycache__` and the
  other directories in `mdix.vault.DEFAULT_IGNORED_DIRS`.

## When a name is ambiguous

`people/overview.md` and `projects/overview.md` both answer to `[[overview]]`. Obsidian links to
the file "closest to the current one"; it does not publish the tie-break, so `mdix` uses a
deterministic reading of it. Candidates are ordered by:

1. same folder as the source note first
2. then the longest shared folder prefix with the source note
3. then the shallowest path
4. then lexicographic order

```bash
mdix links resolve "[[overview]]" --from people/ada-lovelace.md    # people/overview.md
mdix links resolve "[[overview]]" --from projects/overview.md      # projects/overview.md
mdix links resolve "[[overview]]"                                  # people/overview.md (no source: shallowest, then A-Z)
```

`links resolve` always reports the full `candidates` list, best match first, so ambiguity stays
visible instead of being silently decided:

```json
{"resolved": "people/overview.md", "via": "basename",
 "candidates": ["people/overview.md", "projects/overview.md"]}
```

If ambiguity bothers you, the fix is in the vault, not in the tool: rename one of the notes, or
link it by path.

## Scoping the scan

`links ls` and `links unresolved` take the same `--include`/`--exclude` glob filters as
`schema validate`, matched against paths relative to `--root`, include first and exclude after.

The filters decide which notes are **scanned**. Every note in the vault stays a possible
destination, so excluding a folder never turns links *into* it unresolved:

```bash
# templates hold placeholder links; keep them out of the frontier
mdix links unresolved --exclude "_templates/**"

# only the links written in one collection
mdix links ls --include "people/**"
```

`links resolve` has no filters: it resolves one target against the whole vault, and there is
nothing to scope.

## The frontier: links with no note behind them

`mdix links unresolved` is the list of notes you have referred to but not written, ranked by how
many notes are waiting for them:

```bash
$ mdix links unresolved --human
3  thermal-runaway
   - concepts/cycle-life.md
   - technologies/lithium-ion-battery.md
   - technologies/solid-state-battery.md
2  byd
   - companies/tesla-energy.md
   - technologies/lithium-ion-battery.md
1  sodium-ion-battery
   - companies/catl.md
```

Per row:

- `target` - the spelling most notes use (ties go to the alphabetically first)
- `variants` - every spelling seen, since targets are grouped case- and whitespace-insensitively:
  `[[Punch Card]]` and `[[punch card]]` are one row, one future note
- `count` - how many **notes** link it (not how many times)
- `occurrences` - how many link occurrences in total
- `sources` - the notes that link it, sorted

Rows are sorted by `count` descending, then `occurrences`, then target.

**An unresolved link is a request, not an error.** `links unresolved` exits 0 whatever it finds.
Writing `[[sodium-ion-battery]]` before that note exists is how you queue the note, and how
Obsidian shows it in the graph. If you do want a CI gate, build it yourself:

```bash
test "$(mdix links unresolved | jq length)" -le 20
```

## Headings and blocks

`[[Complex I#N module]]` resolves to `Complex I.md` whether or not that note has an `N module`
heading, because Obsidian opens the note either way. A vault that queues sections the way it
queues notes wants to know the difference. `--subpaths` on `resolve`, `ls` and `unresolved`
checks it:

```bash
mdix links resolve "[[Complex I#N module]]" --subpaths      # "subpath_found": false, exit 1
mdix links ls --from genes/NDUFS4.md --subpaths --human      # "... missing #N module" per link
mdix links unresolved --subpaths --human                     # owed notes and owed sections
```

What counts:

- **Headings** are ATX headings, `#` to `######`, outside frontmatter and fenced code. Closing
  `#`s are dropped. The comparison is the one for note names: case-insensitive, whitespace
  collapsed, NFC. Setext headings (underlined with `===` or `---`) are not read.
- **Nested headings**, `#Structure#Q module`, need every heading in the chain to exist. Their
  order is not checked.
- **Blocks**, `#^pump`, need a line ending in `^pump`.
- A link to an attachment, or a link whose note does not exist, has nothing to check:
  `subpath_found` is `null`.

`ls --subpaths` adds `subpath_found` to every record, and `--unresolved-only` then also keeps the
links whose subpath is missing. `unresolved --subpaths` adds one row per missing `note#subpath`,
grouped case-insensitively and ranked together with the missing notes. Such a row has two extra
fields, `note` (the destination that exists) and `subpath`:

```json
{"target": "Complex I#N module", "note": "complexes/Complex I.md", "subpath": "#N module",
 "count": 2, "occurrences": 3, "sources": ["genes/NDUFS4.md", "genes/NDUFV1.md"],
 "variants": ["Complex I#N module", "complex i#n module"]}
```

Without `--subpaths` every command prints exactly what it printed before.

## Working loop

```bash
# 1. what does the vault want next?
mdix links unresolved --human | head -20

# 2. write that note, then check it landed
mdix links resolve "[[thermal-runaway]]"

# 3. check the new note's own links before committing
mdix links ls --from concepts/thermal-runaway.md --human

# 4. anything still dangling, as path:line pairs
mdix links ls --unresolved-only | jq -r '.[] | "\(.path):\(.line) \(.target)"'
```

Links that used to resolve and no longer do are the same list read the other way round: after
renaming or moving a note, `mdix links unresolved` shows every link the rename broke.
