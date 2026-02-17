# `fm show` output shape

A note without frontmatter returns `frontmatter: null` and no errors.

```bash
uv run mdix --root "$VAULT_ROOT" fm show subjects/chemistry.md
```

```expected
{"errors": [], "frontmatter": null, "path": "subjects/chemistry.md"}
```

Malformed frontmatter is reported in structured `errors`.

```bash
uv run mdix --root "$VAULT_ROOT" fm show media/broken-frontmatter.md
```

```expected
{"errors": [{"message": "while parsing a flow sequence\n  in \"<unicode string>\", line 4, column 7\ndid not find expected ',' or ']'\n  in \"<unicode string>\", line 5, column 1", "type": "yaml_error"}], "frontmatter": null, "path": "media/broken-frontmatter.md"}
```
