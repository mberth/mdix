# links resolution and the unresolved frontier

*2026-09-22T08:57:55Z by Showboat 0.6.1*
<!-- showboat-id: 5c3b575a-76e9-465e-a477-59650e82c7a0 -->

Resolution reports the note a link points at and the rule that matched.

```bash
uv run mdix --root 'tests/fixtures/vault_links' links resolve '[[ada-lovelace]]'
```

```output
{"candidates": ["people/ada-lovelace.md"], "display": null, "from": null, "resolved": "people/ada-lovelace.md", "subpath": null, "target": "ada-lovelace", "via": "basename"}
```

An ambiguous name resolves to the note in the source note's folder; every candidate is reported, best match first.

```bash
uv run mdix --root 'tests/fixtures/vault_links' links resolve '[[overview]]' --from projects/analytical-engine.md
```

```output
{"candidates": ["projects/overview.md", "people/overview.md"], "display": null, "from": "projects/analytical-engine.md", "resolved": "projects/overview.md", "subpath": null, "target": "overview", "via": "basename"}
```

A name that matches no file resolves to nothing, and the command exits 1.

```bash
uv run mdix --root 'tests/fixtures/vault_links' links resolve '[[difference-engine]]'; echo "exit=$?"
```

```output
{"candidates": [], "display": null, "from": null, "resolved": null, "subpath": null, "target": "difference-engine", "via": null}
exit=1
```

Listing the links of one note shows targets, subpaths, display text and embeds. Links in fenced code blocks and inline code are not links.

```bash
uv run mdix --root 'tests/fixtures/vault_links' --human links ls --from people/ada-lovelace.md
```

```output
people/ada-lovelace.md:9: analytical-engine -> projects/analytical-engine.md (basename)
people/ada-lovelace.md:11: overview -> people/overview.md (basename)
people/ada-lovelace.md:13: ../projects/analytical-engine -> projects/analytical-engine.md (relative_path)
people/ada-lovelace.md:15: Punch Card -> - (unresolved)
people/ada-lovelace.md:23: diagram.png -> attachments/diagram.png (basename)
```

The frontier: link targets with no note behind them, ranked by how many notes ask for them.

```bash
uv run mdix --root 'tests/fixtures/vault_links' links unresolved --human
```

```output
2  punch card
   - people/ada-lovelace.md
   - projects/analytical-engine.md
1  difference-engine
   - index.md
```
