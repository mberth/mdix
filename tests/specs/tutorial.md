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
