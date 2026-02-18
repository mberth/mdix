# Why I built mdix

My setup for Markdown knowledge bases looks like this:

- one Markdown file per entity
- YAML frontmatter for metadata, including wikilinks between entities
- nested directories and tags for organization and workflows
- Obsidian as a human-friendly user interface for the knowledge base
- an agent like Claude or OpenClaw with tools for web research and local file access
- instructions and note templates for repeatable agent behavior
- git for version control and reviewable history

The agent can answer questions by searching and reading Markdown files.
Humans and agents collaborate on growing and curating the knowledge base.
Structure emerges organically as you learn more about the subject. For example, you add new metadata fields, refine agent instructions, and expand note templates.

## The problem in real knowledge bases

Over time, this workflow accumulates drift:

- filenames follow mixed conventions (case, separators, language variants, legacy names)
- frontmatter keys diverge (`type` vs `kind`, nested vs flat fields, renamed keys)
- value vocabularies become inconsistent (`active`, `identified`, `is_identified`)
- null and partial metadata silently propagate into new notes

This eventually makes agent behavior less reliable, search and filtering noisier, and automation harder to trust.

## How mdix helps

With mdix and unix command line tools, you get an agent-friendly interface for your knowledge base.

mdix makes it easy to:

- validate current metadata state
- preview changes with dry-runs
- apply scoped normalization passes you can review and commit cleanly

mdix works well with Obsidian-style vaults, but it is not tied to Obsidian.
