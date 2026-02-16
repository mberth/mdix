# Development

- We use uv for dependency management
- Use click for command line tools

## Issue Tracking

This project tracks work in-repo using markdown files under `plan/issues/`.

Each issue is a `*.md` file with YAML frontmatter (at minimum):
- `id`
- `title`
- `type` (usually `task`)
- `status` (e.g. `open`, `in_progress`, `done`)
- `priority` (e.g. `P0`-`P4`)
- `labels` (YAML list)

**Quick reference:**
- Create a new issue: add a new file in `plan/issues/` (copy an existing issue as a template)
- Update status: edit the issue frontmatter (`status: ...`)
- Close work: set `status: done` and ensure the implementation is merged and pushed
- Seed initial issues: run `./create_initial_beads_issues.sh` (it writes to `plan/issues/`)

# Writing

When generating markdown:

- Use "-" for list items
- Do not separate sections with horizontal lines
- Use emojis sparingly, prefer black and white over color

General writing guidelines:

- Tone: be a competent technical writer 

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Update `status:` in `plan/issues/*.md` for finished and in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
