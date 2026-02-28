# fm normalize batch frontmatter cleanup

*2026-02-28T16:06:36Z by Showboat 0.6.1*
<!-- showboat-id: e8398b9e-fe22-44ca-a1cd-8738e9161367 -->

fm normalize supports deterministic dry-run previews for repeatable cleanup operations.

```bash
uv run mdix --root 'tests/fixtures/vault_schema_drift' fm normalize --dry-run --include 'people/missing-type.md' --map-value status lead identified --set-default type person --derive-from-filename slug
```

```output
{"changes": [{"changes": [{"field": "status", "from": "lead", "op": "value_map", "to": "identified"}, {"field": "type", "op": "set_default", "value": "person"}, {"field": "slug", "op": "derive_from_filename", "value": "Missing Type"}], "path": "people/missing-type.md", "status": "preview"}], "summary": {"dry_run": true, "files_changed": 1, "files_scanned": 1, "operations": 3, "parse_errors": 0, "skipped_no_frontmatter": 0}}
```
