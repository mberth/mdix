# Development checklist

## Publish for `uvx` (PyPI release)

Use this checklist when releasing `mdix` so it is available via `uvx mdix ...`.

- [ ] Ensure PyPI account access is working and a valid API token is available as `UV_PUBLISH_TOKEN`
- [ ] Bump `version` in `pyproject.toml` (PyPI does not allow re-uploading the same version)
- [ ] Build distributions: `uv build`
- [ ] Optionally verify artifacts exist in `dist/` (`.tar.gz` and `.whl`)
- [ ] Publish to PyPI: `uv publish`
- [ ] Verify install/run via `uvx`: `uvx --refresh mdix --help`
- [ ] Tag the release in git (optional but recommended for traceability)
