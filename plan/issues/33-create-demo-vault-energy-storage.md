---
id: mdix-33
title: "Create demo vault: energy storage knowledge base"
type: task
status: done
priority: P2
parent: null
depends_on: []
labels:
  - demo
  - knowledge-base
  - docs
---

## Goal

Create a realistic, self-contained demo knowledge base about electricity energy storage solutions under `src/mdix/_examples/energy_storage/`. The vault should showcase the `mdix` workflow described in `WHY.md` and `README.md`: structured Markdown notes with frontmatter, a schema, and agent-ready instructions.

## Scope

**In scope:**
- Create `src/mdix/_examples/energy_storage/` with one subdirectory per entity type
- Write a handful of realistic notes (3-5 per entity type) covering energy storage topics
- Add `mdix.schema.yml` in the vault root defining required frontmatter fields and enums
- Add `src/mdix/_examples/energy_storage/INSTRUCTIONS.md` for a research agent to use as an entry point
- Entity types chosen by the implementer (see Notes below for suggestions)

**Out of scope:**
- Exhaustive coverage of the topic (this is a demo, not a reference database)
- Integration tests for the demo vault (the fixture vault under `tests/` covers that)
- Any `mdix` code changes

## Acceptance criteria

- `src/mdix/_examples/energy_storage/` exists and is committed
- At least 3 entity-type subdirectories, each with at least 3 notes
- Every note has valid YAML frontmatter consistent with `mdix.schema.yml`
- `mdix --root src/mdix/_examples/energy_storage schema validate` exits 0 (no violations)
- `INSTRUCTIONS.md` exists and covers:
  - vault structure (folders, entity types, note conventions)
  - how to add a new note (filename convention, required frontmatter fields)
  - how to use `mdix` to inspect and validate the vault
  - how to use the available web search tools (Brave, Perplexity) to research topics
  - what "done" looks like for a research note
- Notes contain real, useful content (not lorem ipsum); agent may use web search to populate them

## Entity type suggestions

Pick 3-4 of these or invent your own:

- `technologies/` - individual storage technologies (lithium-ion, flow batteries, compressed air, etc.)
- `projects/` - real-world deployments and installations
- `companies/` - manufacturers, developers, utilities
- `concepts/` - key engineering concepts (round-trip efficiency, depth of discharge, energy density, etc.)
- `materials/` - cathode/anode/electrolyte materials
- `standards/` - industry standards and certifications

## Notes / Examples

Suggested frontmatter for a `technologies/` note:

```yaml
---
title: "Lithium-Ion Battery"
type: technology
status: active
tags: ["electrochemical", "mature"]
energy_density_wh_kg: 150-300
round_trip_efficiency_pct: 90-95
---
```

Suggested `mdix.schema.yml`:

```yaml
version: 1
fields:
  title:
    type: string
    required: true
  type:
    type: string
    required: true
    enum: [technology, project, company, concept, material, standard]
  status:
    type: string
    required: true
    enum: [active, draft, deprecated]
```

The agent implementing this issue should:
1. Design entity types and schema first
2. Write `INSTRUCTIONS.md`
3. Research and populate notes using Brave/Perplexity web search
4. Validate with `mdix schema validate` before committing
5. Use other mdix commands as appropriate
6. Write a retrospective on the experience, so we can gather feedback on mdix and the general knowledge base setup

## Retrospective

**What was built:**
4 entity types (technologies, projects, companies, concepts), 17 notes total:
- 5 technologies: lithium-ion, vanadium flow, pumped hydro, solid-state, iron-air
- 4 projects: Hornsdale, Moss Landing, Bath County, Dalian
- 4 companies: Tesla Energy, CATL, Fluence, Form Energy
- 4 concepts: round-trip efficiency, depth of discharge, energy density, cycle life

**What worked well with mdix:**

- `mdix schema validate` caught a real error immediately: the schema field type `list` is not valid (mdix requires `array`). Clear error message, fast feedback loop. This is exactly the kind of drift-catching the tool is designed for.
- The schema setup was low-friction: write `mdix.schema.yml`, run validate, see output. The JSON summary (`files_scanned`, `files_valid`, `violations`) is easy to read and pipe-friendly.
- `MDIX_ROOT` environment variable makes repeated validation commands clean without typing the path every time.

**Friction encountered:**

- The `--root` flag does not exist on `mdix schema validate` (only `MDIX_ROOT` works). The README shows `--root` in several examples, which led to a failed invocation before switching to `MDIX_ROOT`. This is a documentation/UX gap worth fixing.
- No inline help on what field types are allowed in the schema. The error `Field 'tags' has unsupported type 'list'` is clear but discovering the allowed list requires reading source or docs - there's no `mdix schema --help` output listing them.

**Research workflow notes:**

- Perplexity (`user-perplexity-search`) gave good structured overviews but inconsistently returned actual URLs in the first pass. A follow-up call asking explicitly for "sources with URLs" worked better. Brave search was not available in this environment (tool not found).
- Citation discipline matters more than it seems for a knowledge base. One note had the wrong date for the Moss Landing fire (I wrote 2022; it was January 2025) and the wrong partial owner for Bath County (wrote LS Power; correct is 40% FirstEnergy). Web search caught both before commit.
- The citation round-trip (Perplexity → get URLs → inline into notes) adds meaningful time. Worth standardizing: ask for sources with URLs in the initial query rather than in a follow-up.

**Suggested follow-up issues:**

- Fix `--root` flag inconsistency in CLI/docs (README shows `--root`, CLI only accepts `MDIX_ROOT`)
- Add allowed field types to schema validation help or docs
- Consider adding a `mdix schema check-file` command for validating a single note before adding it to the vault
