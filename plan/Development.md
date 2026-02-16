## Development guidelines

## Testing

### Tooling
- Use `pytest`.
- Prefer tests that exercise behavior end-to-end via the CLI entrypoint (i.e. running `mdix`), with a small on-disk example vault fixture.

### Running tests
- Sync the environment:
  - `uv sync`
- Run tests:
  - `uv run pytest`
- Run a single test (example):
  - `uv run pytest -k test_name`

### Preferred: end-to-end tests with an example vault
- **Goal**: Treat tests as black-box checks of `mdix` behavior over a real vault on disk.
- **Approach**:
  - Keep a committed fixture vault under `tests/fixtures/`.
  - In each test, copy the fixture vault into `tmp_path` and point `mdix` at that temp copy (never mutate the committed fixture in-place).
  - Use stable assertions (sort outputs; don’t depend on filesystem iteration order).
  - Assert on machine-friendly output (`--json` / JSON output) whenever possible.

### Example fixture vault theme: great scientific discoveries
- **Theme**: Great scientific discoveries.
- **Pages**:
  - `people/` (scientists)
  - `discoveries/` (discoveries / theories / experiments)
  - `subjects/` (fields and topics)
  - `media/` (articles, videos, talks about the above)

### Suggested fixture structure (committed)
- `tests/fixtures/vault_great_discoveries/`
  - `people/`
  - `discoveries/`
  - `subjects/`
  - `media/`

### Suggested note conventions (fixture + future real vaults)
- **Paths are identifiers**: Prefer stable, lowercase, hyphenated filenames (e.g. `people/marie-curie.md`).
- **Frontmatter is optional but encouraged** for tests that cover metadata features.
- **Use simple, consistent fields** in the fixture:
  - `title`: human title
  - `type`: one of `person`, `discovery`, `subject`, `media`
  - `tags`: list of strings (optional)
  - `status`: e.g. `active` / `draft` (optional)

### Minimal example note (illustrative)
```yaml
---
title: "Marie Curie"
type: person
tags: ["physics", "chemistry"]
---
```

### What an end-to-end test should look like (high level)
- Arrange: copy `tests/fixtures/vault_great_discoveries` to a temp dir
- Act: run `uv run mdix --root <temp-vault> <command> ...`
- Assert: verify deterministic output and key fields/content
