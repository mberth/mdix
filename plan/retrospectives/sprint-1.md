---
id: mdix-retro-sprint-1
title: "Retrospective: Sprint 1"
date: 2026-02-16
---

## What we set out to do
- Make `mdix` marginally useful for managing the repo's own issues in `plan/issues/`.
- Establish a lightweight testing approach (pytest + CLI end-to-end checks).

## Where we are (testing status)
- `uv run pytest` passes locally.
- We have CLI-driven end-to-end tests (via `uv run mdix ...`) in `tests/test_frontmatter_errors.py`.
- Gap vs `plan/Development.md` testing guidance:
  - No committed fixture vault under `tests/fixtures/` yet.
  - Coverage is very small (2 tests, focused on one failure mode).
  - No CI workflows found (e.g. GitHub Actions) to run tests on every push/PR.
  - `pyproject.toml` declares `requires-python = ">=3.14"`, but tests currently run under Python 3.11 via `uv run` (version policy mismatch).

## Notes from issues and git history
- The core Sprint 1 slice shipped in one large commit (CLI scaffold + `ls`/`find`/`q`/`fm show` + regression tests), which was efficient but made it easy for docs/acceptance criteria to drift.
- We immediately had to file follow-up “docs/CLI mismatch” issues:
  - `README.md` currently documents unimplemented or incorrect usage (`q` positional expressions, `--where`, `--text`, `--json`, and `mdix fm <path>` vs `mdix fm show <path>`).
  - Root-relative path conventions were easy to get wrong in acceptance criteria (e.g. `--root plan/issues` returns paths like `00-sprint-1-self-manage-issues.md`, not `plan/issues/...`).
- Exit-code conventions are emerging:
  - `mdix find` returns non-zero when no matches (observed exit code 1), which is good for scripting but should be explicitly documented and tested where it matters.
- Status hygiene needs a tighter loop:
  - Several Sprint 1 issues are marked `done`, but later issues indicate their acceptance criteria/examples were inaccurate (so “done” sometimes meant “implemented” rather than “matches documented contract”).
  - The Sprint epic (`mdix-00`) is still `status: open` even though most child tasks are `done` and the remaining work is mostly docs/polish.

## What went well
- The CLI-first testing pattern works: black-box tests calling `mdix` catch behavior and output schema issues cleanly.
- Tests are fast and easy to run (`uv run pytest`).
- The repo docs now capture common issue-management command recipes, which reduces “how do I…?” friction.

## What didn’t go well / surprises
- Python version policy is unclear/inconsistent (declared 3.14+, observed 3.11 in use).
- Testing “definition of done” is under-specified beyond “pytest exists”:
  - No fixture vault means we’re not exercising realistic vault structures yet.
  - No CI means we can regress without noticing until later.

## Countermeasures (proposed)
- Docs drift (README vs implementation)
  - Add a lightweight **docs/CLI contract checklist** to `AGENTS.md` “Landing the Plane”:
    - If CLI behavior changed, run copy/paste checks for every command shown in `README.md`.
    - Prefer examples that use only currently implemented flags/subcommands.
  - Add a small “**Examples must be executable**” rule to `plan/Development.md`:
    - Examples should be written exactly as they’re meant to be run (including `fm show`).
    - When `--root` is used, examples must reflect root-relative paths in output.
  - (Later) Add a **doctest-style smoke test** that runs the README examples that we claim work (or a curated subset).

- Acceptance-criteria drift (“done” ≠ “matches documented contract”)
  - Update the issue template guidance in `plan/Development.md`:
    - Acceptance criteria should include at least one **copy/paste CLI invocation** plus an assertion about output shape (JSON list vs object, key names, path relativity).
    - For anything involving output paths, explicitly state “**paths are relative to `--root`**”.
  - Add a “**definition of done includes docs alignment**” note:
    - A task is only `done` when implementation + docs/examples/AC match.

- Status hygiene / epic closure
  - Add a cadence rule in `AGENTS.md`:
    - When closing a work session, update `status:` fields for the issues you touched and, if appropriate, the epic.
  - Add a “**Sprint close-out**” mini-checklist (could live in `plan/Development.md`):
    - Epic `status: done` once child issues are done and remaining work is explicitly filed as follow-up issues (docs/polish/tech debt).

- Python version policy mismatch
  - Decide a supported version range and make it consistent across:
    - `pyproject.toml` `requires-python`
    - `uv`/dev instructions in `README.md`
    - CI configuration (once added)
  - Add a quick “**version policy**” paragraph to `plan/Development.md` (why we chose it, and how to upgrade).

- Missing fixture vault + thin test coverage
  - Implement the `src/mdix/_examples/vault_great_discoveries/` plan from `plan/Development.md` and require new features to add at least one fixture-driven E2E test.
  - Add a couple “high-signal” regression tests:
    - `q` outputs a JSON list and is deterministic
    - `ls --has` semantics with `null` values
    - `find` exit codes (match vs no match)

- Missing CI
  - Add a minimal CI workflow that runs `uv sync` and `uv run pytest` on push/PR.
  - Make CI the arbiter for “done”: if CI fails, the related issue cannot be `done`.

## Action items (proposed)
- Add CI to run `uv run pytest` on push/PR (and pin an explicit supported Python version range).
- Add `src/mdix/_examples/vault_great_discoveries/` and migrate/add tests to use it (per `plan/Development.md`).
- Expand coverage for the Sprint 1 issue workflows:
  - `ls` determinism and `--has fm.<field>`
  - `fm show` schema stability (including missing/empty frontmatter)
  - `find` behavior and output determinism
  - `q` output shape (frontmatter/errors present, stable ordering)
- Decide and document Python support:
  - Either lower `requires-python` to what we actually use, or adopt 3.14+ intentionally and enforce it in CI/dev setup.

