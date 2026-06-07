# Codex Skillsmith Instructions

This repository stores reusable Codex skills.

## Repository Layout

- `skills/<skill-name>/SKILL.md`: required skill instructions with YAML frontmatter.
- `skills/<skill-name>/agents/openai.yaml`: optional UI metadata.
- `scripts/`: repository maintenance and validation scripts.

## Rules

- Keep skills concise and procedural.
- Do not commit private Codex chat contents, secrets, tokens, private local paths, student data, or personal records.
- Prefer reusable instructions over one-off notes.
- Add helper scripts only when they reduce repeated manual work or improve validation reliability.
- Validate skills before committing with `ruby scripts/validate_skills.rb`.

## Definition of Done

- Skill frontmatter parses and includes `name` and `description`.
- Optional UI metadata parses.
- README is updated when layout, install steps, or validation changes.
- Public commits contain no private data or secrets.
