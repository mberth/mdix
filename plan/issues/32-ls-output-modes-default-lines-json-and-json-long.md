---
id: mdix-32
title: "Update mdix ls output modes: default line output plus --json and --json-long"
type: task
status: open
priority: P1
parent: null
depends_on: []
labels:
  - cli
  - ls
  - output
  - unix
---

## Goal
Make `mdix ls` follow Unix-friendly defaults: plain line output by default (one file path per line), with explicit structured output modes for automation via `--json` and `--json-long`.

## Scope
- Change `mdix ls` default output to simple lines, one path per line.
- Make `mdix ls --human` produce the same output as the default mode (alias behavior).
- Add `mdix ls --json` to return a JSON array of file paths.
- Add `mdix ls --json-long` to return a JSON array of records including `path`, `ctime`, `mtime`, and `size`.
- Update help text and README examples to reflect the new mode contract.
- Add/adjust regression tests for all `ls` output modes.

## Acceptance criteria
- `mdix ls` prints one file path per line with deterministic ordering and no extra formatting.
- `mdix ls --human` matches default output exactly.
- `mdix ls --json` returns a JSON list of file paths (strings), suitable for tooling.
- `mdix ls --json-long` returns a JSON list of objects, each containing:
  - `path`
  - `ctime`
  - `mtime`
  - `size`
- Running `mdix ls --human` no longer errors with:
  - `No such option: --human`
- `mdix ls -h` documents all supported output flags (`--human`, `--json`, `--json-long`) and their semantics.
- Existing commands that pipe `mdix ls` into shell tools (`grep`, `wc -l`, `xargs`) work without requiring `--human`.

## Notes / Examples
- Desired behavior examples:
  - `mdix ls` -> plain lines
  - `mdix ls --human` -> same plain lines
  - `mdix ls --json` -> `["a.md", "b/c.md"]`
  - `mdix ls --json-long` -> `[{"path":"a.md","ctime":"...","mtime":"...","size":123}]`
- Consider backward compatibility carefully if any docs/tests still assume default JSON output from `mdix ls`.
