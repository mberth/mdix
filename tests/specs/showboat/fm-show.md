# fm show output shape

*2026-02-28T16:06:39Z by Showboat 0.6.1*
<!-- showboat-id: 6b3eaec7-bcc0-44e7-9206-72dddacb1fc6 -->

A note without frontmatter returns frontmatter null and no errors.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries' fm show subjects/chemistry.md
```

```output
{"errors": [], "frontmatter": null, "path": "subjects/chemistry.md"}
```

Malformed frontmatter is reported in structured errors.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries' fm show media/broken-frontmatter.md
```

```output
{"errors": [{"message": "while parsing a flow sequence\n  in \"<unicode string>\", line 4, column 7\ndid not find expected ',' or ']'\n  in \"<unicode string>\", line 5, column 1", "type": "yaml_error"}], "frontmatter": null, "path": "media/broken-frontmatter.md"}
```
