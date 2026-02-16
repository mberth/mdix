---
id: mdix-11
title: "Bug: Docs/examples imply wrong path prefixes and unclear --has null semantics"
type: task
status: open
priority: P2
parent: mdix-00
depends_on: []
labels:
  - sprint-1
  - docs
  - bug
  - frontmatter
---

## Goal
Align docs and issue examples with the actual “paths are relative to `--root`” behavior, and clarify what `mdix ls --has fm.<field>` means when the field exists but is `null`.

## Scope
- Update Sprint 1 doc examples (and any issue acceptance criteria that mention prefixed paths) to match current output conventions
- Clarify/document `--has fm.<field>` semantics:
  - it checks key presence in frontmatter (not “non-null” / “truthy” value)
  - `null` still counts as “present” if the key exists
- Add a short “how to filter non-null” note using `mdix q | jq` (no new CLI features required)

## Acceptance criteria
- Examples using `mdix --root plan/issues ...` do not claim outputs include `plan/issues/` prefixes
  - For example, `mdix --root plan/issues ls --has fm.parent` is documented as returning paths like `00-sprint-1-self-manage-issues.md`
- `plan/issues/05-ls-has.md` acceptance criteria does not require `plan/issues/...` in output when `--root plan/issues` is used
- Docs state explicitly that `--has fm.parent` matches files where `parent:` exists even if it is `null`
- Docs include an example for “non-null parent” filtering via `mdix --root plan/issues q | jq ...`

## Notes
- Observed current behavior:
  - `uv run mdix --root plan/issues ls --has fm.parent` returns all issue files because they all have a `parent` key (some are `null`)
  - Output paths are relative to `--root` (e.g. `00-sprint-1-self-manage-issues.md`)

