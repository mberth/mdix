# `ls` deterministic output

The `ls` command returns a stable, sorted list of markdown files.

```bash
uv run mdix --root "$VAULT_ROOT" ls
```

```expected
["discoveries/general-relativity.md", "discoveries/problematic-content-key.md", "discoveries/radioactivity.md", "media/broken-frontmatter.md", "media/einstein-1915-paper.md", "people/albert-einstein.md", "people/marie-curie.md", "subjects/chemistry.md", "subjects/physics.md"]
```

When filtering by frontmatter field presence, results remain deterministic.

```bash
uv run mdix --root "$VAULT_ROOT/people" ls --has fm.status
```

```expected
["albert-einstein.md", "marie-curie.md"]
```
