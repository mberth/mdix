# Development checklist

## Publish for `uvx` (PyPI release)

Releases go out through the manually triggered `Publish to PyPI` workflow
(`.github/workflows/publish.yml`). It uses PyPI trusted publishing, so no token is stored in the repo.

One-time setup:

- On PyPI, open the `mdix` project, then Publishing -> Add a new publisher -> GitHub, with owner `mberth`,
  repository `mdix`, workflow `publish.yml`, environment `pypi`
- On GitHub, create the environment `pypi` (Settings -> Environments). Add yourself as a required
  reviewer if you want a confirmation click before the upload

Each release:

- [ ] Bump `version` in `pyproject.toml` and run `uv lock`, in a PR merged to `master`
- [ ] Actions -> Publish to PyPI -> Run workflow, on `master`
- [ ] The workflow refuses a version that is already on PyPI or already tagged, runs lint and tests,
  builds, uploads, and tags the commit `v<version>`
- [ ] Verify install/run via `uvx`: `uvx --refresh mdix --help`

Manual fallback: `uv build`, then `uv publish` with a PyPI token in `UV_PUBLISH_TOKEN`, then tag the commit.
