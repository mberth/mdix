# ls deterministic output

*2026-02-28T16:06:43Z by Showboat 0.6.1*
<!-- showboat-id: 8daa4a31-1424-4f57-a1a4-9e2a42bdfaf9 -->

The ls command returns a stable, sorted list of markdown files.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries' ls
```

```output
["discoveries/general-relativity.md", "discoveries/problematic-content-key.md", "discoveries/radioactivity.md", "media/broken-frontmatter.md", "media/einstein-1915-paper.md", "people/albert-einstein.md", "people/marie-curie.md", "subjects/chemistry.md", "subjects/physics.md"]
```

When filtering by frontmatter field presence, results remain deterministic.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries/people' ls --has fm.status
```

```output
["albert-einstein.md", "marie-curie.md"]
```
