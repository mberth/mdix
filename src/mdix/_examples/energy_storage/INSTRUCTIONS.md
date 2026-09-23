# Energy Storage Knowledge Base - Agent Instructions

This vault is a research knowledge base about electricity energy storage: technologies, real-world projects, companies, and engineering concepts. It is designed for humans and AI agents to read, search, and extend together.

## Vault structure

```
energy_storage/
  mdix.schema.yml         # frontmatter schema for all notes
  INSTRUCTIONS.md         # this file
  technologies/           # storage technology notes (lithium-ion, flow batteries, etc.)
  projects/               # real-world deployments and installations
  companies/              # manufacturers, integrators, and developers
  concepts/               # engineering and economic concepts
```

Each subdirectory contains one Markdown file per entity. Filenames use lowercase kebab-case (e.g., `lithium-ion-battery.md`, `hornsdale-power-reserve.md`).

## Frontmatter conventions

Every note must have valid YAML frontmatter satisfying `mdix.schema.yml`. Required fields:

- `title` (string) - full readable name
- `type` (string) - must be one of: `technology`, `project`, `company`, `concept`
- `status` (string) - must be one of: `active`, `draft`, `deprecated`
- `tags` (array, optional) - lowercase kebab-case strings for cross-cutting themes

Type-specific optional fields (not enforced by schema, but use consistent keys across notes of the same type):

**technology**: `energy_density_wh_kg`, `round_trip_efficiency_pct`, `typical_duration_hours`, `maturity` (`research` | `pilot` | `commercial` | `mature`)

**project**: `location`, `capacity_mwh`, `power_mw`, `technology` (wikilink string), `year_commissioned`

**company**: `hq`, `focus` (list)

## How to add a new note

1. Choose the correct subdirectory based on `type`.
2. Name the file using lowercase kebab-case, e.g., `sodium-sulfur-battery.md`.
3. Write the frontmatter block first, filling all required fields.
4. Write the body in Markdown. Aim for 200-500 words of real, useful content.
5. Cite your sources (see below).
6. Validate before committing:
   ```bash
   mdix schema validate
   ```

## Citation requirements

**Every factual claim - numbers, dates, ownership, capacity figures, cost data - must be cited.**

Use inline Markdown hyperlinks directly in the text, at the point where the fact appears:

```markdown
The facility has a total capacity of [150 MW / 193.5 MWh](https://en.wikipedia.org/wiki/Hornsdale_Power_Reserve).
```

Or group citations at the end of a paragraph:

```markdown
Bath County has a maximum generating capacity of 3,003 MW and stores 24,000 MWh.
([Wikipedia](https://en.wikipedia.org/wiki/Bath_County_Pumped_Storage_Station), [Dominion Energy](https://www.dominionenergy.com/projects-and-facilities/hydroelectric-power-facilities-map/bath-county-pumped-storage-station))
```

For a block of related facts from one source, add a **Sources** section at the bottom:

```markdown
## Sources

- [Wikipedia: Hornsdale Power Reserve](https://en.wikipedia.org/wiki/Hornsdale_Power_Reserve)
- [ARENA project summary](https://arena.gov.au/knowledge-bank/neoen-hornsdale-power-reserve-upgrade-project-summary-report/)
```

**What counts as adequate citation:**
- Figures (MW, MWh, %, $/kWh, year): always cite
- Named events (fires, contract awards, milestones): cite with a news article or press release
- Technology principles and physics: Wikipedia is fine
- Company descriptions and ownership: company IR pages, SEC filings, or reputable news
- Market share and pricing: cite analyst sources (BloombergNEF, SNE Research, BNEF, Wood Mackenzie) when available

**Prefer:**
1. Primary sources (operator/manufacturer pages, regulator filings, ARENA/DOE/IEA reports)
2. Reputable news (Utility Dive, PV Magazine, Canary Media, Energy-Storage.news)
3. Wikipedia for stable engineering facts - link to the specific article

Do not assert facts without a source link. If you cannot find a source for a number, flag it with `[citation needed]` rather than including it uncited.

## Researching new notes

Use available web search tools to gather facts:

- **Perplexity** (`user-perplexity-search`) - good for structured overviews and quick fact-checking
- **Brave web search** (`user-brave_web_search`) - useful for recent news and finding primary source URLs

Workflow for a new technology or project note:
1. Search Perplexity for an overview to understand key facts and relationships.
2. Search Brave or fetch URLs to find primary sources (operator site, Wikipedia, IEA/ARENA/DOE reports).
3. Write the note, citing every figure inline.
4. Cross-link to related notes using `[[wikilink]]` syntax. Link entities that have no note yet too -
   `mdix links unresolved` turns those into the queue for the next note.

## Using mdix to inspect the vault

```bash
# Validate all notes against the schema
mdix schema validate

# List all notes with their frontmatter as JSON
mdix q | jq '.[] | {path, type: .frontmatter.type, status: .frontmatter.status}'

# Find notes mentioning a term
mdix find "round-trip efficiency"

# Inspect frontmatter on a specific note
mdix fm show technologies/lithium-ion-battery.md

# Check for drift across the vault
mdix schema inventory | jq '.summary'

# See which notes are missing: link targets with no note behind them
mdix links unresolved --human

# Check the links of a note you just wrote
mdix links ls --from technologies/lithium-ion-battery.md --human
```

## What "done" looks like for a research note

A note is ready to commit when it:

- Passes `mdix schema validate` with no violations
- Has a real title and 200+ words of accurate content
- Cites sources for all numerical claims and key facts with hyperlinks
- Cross-links to at least one related note
- Has no `[citation needed]` placeholders remaining
- Is in a `status: active` (or `draft` if intentionally incomplete)
