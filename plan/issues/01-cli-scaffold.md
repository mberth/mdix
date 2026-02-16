---
id: mdix-01
title: "Scaffold click CLI"
type: task
status: done
priority: P2
parent: mdix-00
depends_on: []
labels:
  - sprint-1
  - mvp
  - cli
---

## Goal
Create the minimal `mdix` CLI skeleton using `click` with consistent flags and help text.

## Scope (first chunk)
- Provide a top-level `mdix` command with `--root` option and `MDIX_ROOT` env var support
- Implement `mdix ls` as recursive enumeration of all md files
- Implement stable, deterministic traversal ordering for anything that walks the filesystem. Like ls -R would do it.
- Establish output conventions:
  - machine-friendly output (JSON/JSONL/lines) is the default
  - `--human` opt-in for pretty text output

## Acceptance criteria
- Running `mdix --help` shows the planned subcommands from README: `q`, `find`, `ls`, `fm show|set|unset|lint`, `new`
all of these with "not yet implemented"
- `mdix --root /path ...` and `MDIX_ROOT=/path mdix ...` point all commands at the same vault root
- Paths in output are stable and deterministic across runs on the same filesystem
- From this repo root, `mdix --root plan/issues q` and `mdix --root plan/issues fm show 00-sprint-1-self-manage-issues.md` both resolve paths under the same root

## Notes
README references uv for dev and click for CLI tooling.
