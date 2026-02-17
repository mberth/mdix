# Tutorial: common knowledge base operations

This walkthrough demonstrates common tasks against the great discoveries fixture vault.

List all notes in deterministic path order:

```bash
uv run mdix --root "$VAULT_ROOT" ls
```

```expected
["discoveries/general-relativity.md", "discoveries/problematic-content-key.md", "discoveries/radioactivity.md", "media/broken-frontmatter.md", "media/einstein-1915-paper.md", "people/albert-einstein.md", "people/marie-curie.md", "subjects/chemistry.md", "subjects/physics.md"]
```

Search for a topic across the whole vault:

```bash
uv run mdix --root "$VAULT_ROOT" find relativity
```

```expected
[{"line": 9, "path": "discoveries/general-relativity.md", "text": "General relativity explains gravitation as the geometry of spacetime."}, {"line": 6, "path": "media/einstein-1915-paper.md", "text": "  - relativity"}, {"line": 9, "path": "media/einstein-1915-paper.md", "text": "The 1915 paper presents the field equations of general relativity."}, {"line": 6, "path": "people/albert-einstein.md", "text": "  - relativity"}, {"line": 10, "path": "people/albert-einstein.md", "text": "Albert Einstein developed the theory of general relativity."}]
```

Scope work to a subfolder and filter to notes with a status field:

```bash
uv run mdix --root "$VAULT_ROOT/people" ls --has fm.status
```

```expected
["albert-einstein.md", "marie-curie.md"]
```

Inspect frontmatter for a single note:

```bash
uv run mdix --root "$VAULT_ROOT" fm show people/marie-curie.md
```

```expected
{"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "chemistry"], "title": "Marie Curie", "type": "person"}, "path": "people/marie-curie.md"}
```

Inspect a note with malformed frontmatter and get structured parse errors:

```bash
uv run mdix --root "$VAULT_ROOT" fm show media/broken-frontmatter.md
```

```expected
{"errors": [{"message": "while parsing a flow sequence\n  in \"<unicode string>\", line 4, column 7\ndid not find expected ',' or ']'\n  in \"<unicode string>\", line 5, column 1", "type": "yaml_error"}], "frontmatter": null, "path": "media/broken-frontmatter.md"}
```

Get an indexed snapshot of the whole vault, including parser errors per file:

```bash
uv run mdix --root "$VAULT_ROOT" q
```

```expected
[{"errors": [], "frontmatter": {"status": "active", "tags": ["physics"], "title": "General Relativity", "type": "discovery"}, "path": "discoveries/general-relativity.md"}, {"errors": [{"message": "Post.__init__() got multiple values for argument 'content'", "type": "frontmatter_error"}], "frontmatter": null, "path": "discoveries/problematic-content-key.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "chemistry"], "title": "Radioactivity", "type": "discovery"}, "path": "discoveries/radioactivity.md"}, {"errors": [{"message": "while parsing a flow sequence\n  in \"<unicode string>\", line 4, column 7\ndid not find expected ',' or ']'\n  in \"<unicode string>\", line 5, column 1", "type": "yaml_error"}], "frontmatter": null, "path": "media/broken-frontmatter.md"}, {"errors": [], "frontmatter": {"tags": ["paper", "relativity"], "title": "Einstein 1915 Paper", "type": "media"}, "path": "media/einstein-1915-paper.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "relativity"], "title": "Albert Einstein", "type": "person"}, "path": "people/albert-einstein.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "chemistry"], "title": "Marie Curie", "type": "person"}, "path": "people/marie-curie.md"}, {"errors": [], "frontmatter": null, "path": "subjects/chemistry.md"}, {"errors": [], "frontmatter": {"tags": ["science"], "title": "Physics", "type": "subject"}, "path": "subjects/physics.md"}]
```

Inspect schema drift on the dedicated schema fixture vault:

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema inventory
```

```expected
{"fields": [{"count": 1, "field": "kontakt"}, {"count": 1, "field": "kontakt.email"}, {"count": 1, "field": "kontakt_email"}, {"count": 2, "field": "position"}, {"count": 1, "field": "rolle"}, {"count": 4, "field": "status"}, {"count": 4, "field": "title"}, {"count": 3, "field": "type"}], "summary": {"distinct_fields": 8, "files_scanned": 4, "files_with_frontmatter": 4, "parse_errors": 0}}
```

Validate against `mdix.schema.yml` (non-strict for demo continuity):

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema validate --no-strict
```

```expected
{"schema": "mdix.schema.yml", "summary": {"files_scanned": 4, "files_valid": 2, "files_validated": 4, "files_with_frontmatter": 4, "files_with_violations": 2, "parse_errors": 0, "violations": 2}, "violations": [{"actual": "active", "code": "SCHEMA_ENUM_MISMATCH", "expected": ["identified", "lead", "zu_kontaktieren"], "field": "status", "message": "Field `status` value is outside allowed enum.", "path": "discoveries/drifted-status.md"}, {"actual": null, "code": "SCHEMA_REQUIRED_MISSING", "expected": {"required": true}, "field": "type", "message": "Missing required field `type`.", "path": "people/missing-type.md"}]}
```

Preview migration transforms safely with dry-run:

```bash
uv run mdix --root "$SCHEMA_DRIFT_ROOT" schema migrate --dry-run
```

```expected
{"changes": [{"changes": [{"from": "rolle", "op": "rename", "to": "position", "value": "Research Lead"}, {"from": "kontakt_email", "op": "rename", "to": "kontakt.email", "value": "alice@example.com"}], "path": "people/alice-example.md", "status": "preview"}], "schema": "mdix.schema.yml", "summary": {"dry_run": true, "files_changed": 1, "files_scanned": 4, "operations": 2, "parse_errors": 0, "skipped_no_frontmatter": 0}}
```
