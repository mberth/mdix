# `fm normalize` batch frontmatter cleanup

`fm normalize` supports deterministic dry-run previews for repeatable cleanup operations.

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" fm normalize --dry-run --include "people/missing-type.md" --map-value status lead identified --set-default type person --derive-from-filename slug
```

```expected
{"changes": [{"changes": [{"field": "status", "from": "lead", "op": "value_map", "to": "identified"}, {"field": "type", "op": "set_default", "value": "person"}, {"field": "slug", "op": "derive_from_filename", "value": "Missing Type"}], "path": "people/missing-type.md", "status": "preview"}], "summary": {"dry_run": true, "files_changed": 1, "files_scanned": 1, "operations": 3, "parse_errors": 0, "skipped_no_frontmatter": 0}}
```
