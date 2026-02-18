---
id: mdix-31
title: "Add Unicode filename normalization checks, docs, and pre-commit guidance"
type: task
status: open
priority: P2
parent: null
depends_on: []
labels:
  - filenames
  - unicode
  - docs
  - pre-commit
---

## Goal
Help vault maintainers detect and prevent visually-duplicate Unicode filenames (NFC vs NFD drift) by adding a dedicated `mdix` command, clear docs, and an actionable pre-commit recommendation.

## Scope
- Add a new `mdix` subcommand focused on Unicode filename normalization auditing (and optionally normalization planning/fixing).
- Document the filename normalization problem with concrete examples (`ü` precomposed vs decomposed) and cross-platform behavior caveats.
- Provide a recommended pre-commit integration for repositories using `mdix`.
- Capture current ecosystem findings so we avoid reinventing a hook that already exists.

## Acceptance criteria
- `mdix` exposes a subcommand that can scan vault paths and report Unicode normalization issues deterministically in JSON/human output.
- The command reports at least:
  - files whose normalized form differs from the stored path
  - collisions where distinct tracked paths normalize to the same canonical form
- README/docs include:
  - a short explanation of NFC vs NFD with one concrete filename example
  - implications for git status/diffs and cross-platform collaboration
  - a remediation workflow using `mdix` output plus `git mv`
- The docs include a pre-commit recommendation that is practical today.
- Tests cover at least one decomposed/precomposed pair and one collision scenario.

## Research notes (existing hooks)
- No broadly-adopted pre-commit hook was found that directly enforces Unicode filename normalization form (NFC/NFD) for git paths.
- Existing CLI tooling does exist for detection/preview and conversion:
  - `convmv` supports normalization targets (`--nfc` / `--nfd`) and dry-run by default, which makes it suitable as an interim checker in hook workflows.
- Relevant references reviewed:
  - Git hooks docs (default sample pre-commit blocks non-ASCII filenames, which is different from normalization checks): `https://git-scm.com/docs/githooks`
  - pre-commit featured hooks list: `https://pre-commit.com/hooks.html`
  - pre-commit-hooks catalog (helpful checks like case conflicts / illegal Windows names, but no NFC/NFD filename normalization check): `https://github.com/pre-commit/pre-commit-hooks`
  - convmv manpage: `https://manpages.debian.org/testing/convmv/convmv.1.en.html`

## Recommended pre-commit path
- Recommend `pre-commit` with a local hook that runs the new `mdix` Unicode filename check command in `--check` mode and fails on findings.
- Until the `mdix` command exists, recommend a local pre-commit check wrapper around `convmv` dry-run output (fail the commit if normalization drift is detected).
- Optionally pair with `pre-commit-hooks` `check-case-conflict` for additional filename portability guardrails.

## Notes / Examples
- Candidate command shapes (to refine during implementation):
  - `mdix lint --check`
  - `mdix lint --json`
  - `mdix lint --fix` (normalizes filenames to nfc)
- Keep behavior deterministic and non-destructive by default; any auto-fix mode should be explicit and dry-run friendly.
- Example `.pre-commit-config.yaml` (interim + target state):

```yaml
repos:
  - repo: local
    hooks:
      # Interim: use convmv dry-run output as a detector.
      - id: unicode-filename-normalization-convmv
        name: Check Unicode filename normalization (NFC)
        language: system
        pass_filenames: false
        entry: bash -c 'out=$(convmv -r -f utf-8 -t utf-8 --nfc . 2>/dev/null); echo "$out"; ! echo "$out" | grep -q "would rename"'

      # Target: switch to mdix once command exists.
      - id: mdix-unicode-filename-check
        name: mdix Unicode filename check
        language: system
        pass_filenames: false
        entry: uv run mdix lint

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-case-conflict
```
