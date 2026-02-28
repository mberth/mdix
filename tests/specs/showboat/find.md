# find deterministic ordering

*2026-02-28T16:06:33Z by Showboat 0.6.1*
<!-- showboat-id: d9e85f38-5030-40a7-b0b6-283034684fb5 -->

find emits deterministic matches in path and line order.

```bash
uv run mdix --root 'tests/fixtures/vault_great_discoveries' find relativity
```

```output
[{"line": 9, "path": "discoveries/general-relativity.md", "text": "General relativity explains gravitation as the geometry of spacetime."}, {"line": 6, "path": "media/einstein-1915-paper.md", "text": "  - relativity"}, {"line": 9, "path": "media/einstein-1915-paper.md", "text": "The 1915 paper presents the field equations of general relativity."}, {"line": 6, "path": "people/albert-einstein.md", "text": "  - relativity"}, {"line": 10, "path": "people/albert-einstein.md", "text": "Albert Einstein developed the theory of general relativity."}]
```
