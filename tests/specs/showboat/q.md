# q output shape and ordering

*2026-02-28T16:06:45Z by Showboat 0.6.1*
<!-- showboat-id: b5ba73f3-0d45-4e82-9cd3-dae15004d8b9 -->

q returns a stable JSON list with path, frontmatter, and errors.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries' q
```

```output
[{"errors": [], "frontmatter": {"status": "active", "tags": ["physics"], "title": "General Relativity", "type": "discovery"}, "path": "discoveries/general-relativity.md"}, {"errors": [{"message": "Post.__init__() got multiple values for argument 'content'", "type": "frontmatter_error"}], "frontmatter": null, "path": "discoveries/problematic-content-key.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "chemistry"], "title": "Radioactivity", "type": "discovery"}, "path": "discoveries/radioactivity.md"}, {"errors": [{"message": "while parsing a flow sequence\n  in \"<unicode string>\", line 4, column 7\ndid not find expected ',' or ']'\n  in \"<unicode string>\", line 5, column 1", "type": "yaml_error"}], "frontmatter": null, "path": "media/broken-frontmatter.md"}, {"errors": [], "frontmatter": {"tags": ["paper", "relativity"], "title": "Einstein 1915 Paper", "type": "media"}, "path": "media/einstein-1915-paper.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "relativity"], "title": "Albert Einstein", "type": "person"}, "path": "people/albert-einstein.md"}, {"errors": [], "frontmatter": {"status": "active", "tags": ["physics", "chemistry"], "title": "Marie Curie", "type": "person"}, "path": "people/marie-curie.md"}, {"errors": [], "frontmatter": null, "path": "subjects/chemistry.md"}, {"errors": [], "frontmatter": {"tags": ["science"], "title": "Physics", "type": "subject"}, "path": "subjects/physics.md"}]
```
