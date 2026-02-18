# Development

- Developer-facing guidelines live in [`plan/Development.md`](plan/Development.md) (tech stack, product principles, testing, and how we write issues).

## Issue Tracking

Project issue format and conventions are documented in [`plan/Development.md`](plan/Development.md) (see “Writing issues (in-repo)”).

## Frontmatter handling

- Do not parse YAML frontmatter by manually splitting on `---` delimiters in ad-hoc scripts.
- Use `python-frontmatter` (or existing `mdix` frontmatter helpers) for read/write operations so behavior stays consistent across tools.

# Writing

When generating markdown:

- Use "-" for list items
- Do not separate sections with horizontal lines
- Use emojis sparingly, prefer black and white over color

General writing guidelines:

- Tone baseline: friendly senior developer who has been there, done that
- Optimize for information transfer: concrete, specific, and operationally useful
- Avoid MBA/consultant phrasing, hype language, and abstract framing
- Prefer plain, direct wording over slogans or "framework" language
- Lead with the real problem and practical outcome
- Use concise sections and bullets that help skimming without sounding robotic
- Keep claims grounded in observable behavior (commands, outputs, constraints, trade-offs)

Examples:

- Less useful: "Leverage a robust metadata governance framework to unlock scalable knowledge operations."
- Better: "Use `mdix schema validate` to find frontmatter drift, then run scoped `mdix fm normalize --dry-run` passes before applying changes."
- Less useful: "Implement strategic standardization for naming consistency."
- Better: "Pick one filename convention and enforce it with small, reviewable cleanup commits."

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Update `status:` in `plan/issues/*.md` for every touched issue:
   - Move active work to `in_progress`
   - Move only fully aligned work to `done` (implementation + tests + docs/examples/acceptance criteria)
   - If follow-up issues expose drift in a `done` issue, move it back to `in_progress`
   - Keep epic status in sync with child statuses (`in_progress` while any child is not done)
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
