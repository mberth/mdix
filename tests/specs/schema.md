# `schema` inventory, validate, migrate

The schema commands support deterministic quality gates and migration previews.

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema inventory
```

```expected
{"fields": [{"count": 1, "field": "kontakt"}, {"count": 1, "field": "kontakt.email"}, {"count": 1, "field": "kontakt_email"}, {"count": 1, "field": "legacy_note"}, {"count": 2, "field": "position"}, {"count": 1, "field": "rolle"}, {"count": 4, "field": "status"}, {"count": 4, "field": "title"}, {"count": 3, "field": "type"}], "summary": {"distinct_fields": 9, "files_scanned": 4, "files_with_frontmatter": 4, "parse_errors": 0}}
```

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema validate --no-strict
```

```expected
{"schema": "mdix.schema.yml", "summary": {"files_scanned": 4, "files_valid": 2, "files_validated": 4, "files_with_frontmatter": 4, "files_with_violations": 2, "parse_errors": 0, "violations": 2}, "violations": [{"actual": "active", "code": "SCHEMA_ENUM_MISMATCH", "expected": ["identified", "lead", "zu_kontaktieren"], "field": "status", "message": "Field `status` value is outside allowed enum.", "path": "discoveries/drifted-status.md"}, {"actual": null, "code": "SCHEMA_REQUIRED_MISSING", "expected": {"required": true}, "field": "type", "message": "Missing required field `type`.", "path": "people/missing-type.md"}]}
```

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema migrate --dry-run
```

```expected
{"changes": [{"changes": [{"field": "status", "from": "active", "op": "value_map", "to": "identified"}, {"field": "legacy_note", "op": "unset_if_null"}], "path": "discoveries/drifted-status.md", "status": "preview"}, {"changes": [{"from": "rolle", "op": "rename", "to": "position", "value": "Research Lead"}, {"from": "kontakt_email", "op": "rename", "to": "kontakt.email", "value": "alice@example.com"}], "path": "people/alice-example.md", "status": "preview"}, {"changes": [{"field": "type", "op": "set_default", "value": "person"}], "path": "people/missing-type.md", "status": "preview"}], "schema": "mdix.schema.yml", "summary": {"dry_run": true, "files_changed": 3, "files_scanned": 4, "operations": 5, "parse_errors": 0, "skipped_no_frontmatter": 0}}
```
