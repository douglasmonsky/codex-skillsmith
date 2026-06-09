# Codex Skillsmith

Reusable Codex skills for improving local Codex workflows.

This repository is a public home for practical skills that start as local workflow improvements and are worth keeping, sharing, and evolving over time.

## Included Skills

- `codex-thread-renamer`: reviews Codex chat titles, scores title quality, suggests better titles, and applies approved renames through supported Codex thread tools.
- `pypi-deploy`: maintainer-only release workflow for preparing, verifying, and publishing Python packages to TestPyPI or PyPI with Trusted Publishing.
- `release-captain`: prepares release notes, validation evidence, risk reviews, smoke tests, and rollback plans before tagging, publishing, or deploying.

## Layout

```text
skills/
  codex-thread-renamer/
    SKILL.md
    agents/openai.yaml
  pypi-deploy/
    SKILL.md
    agents/openai.yaml
  release-captain/
    SKILL.md
    agents/openai.yaml
    scripts/
    references/
    assets/
scripts/
  validate_skills.rb
```

## Validate

Run:

```sh
ruby scripts/validate_skills.rb
```

The validator checks that each skill has valid YAML frontmatter with `name` and `description`, and that optional `agents/openai.yaml` files parse correctly.

## Install Locally

Copy a skill folder into your local Codex skills directory:

```sh
cp -R skills/codex-thread-renamer ~/.codex/skills/
cp -R skills/pypi-deploy ~/.codex/skills/
cp -R skills/release-captain ~/.codex/skills/
```

Restart or reload Codex if the skill list does not update immediately.

## Privacy

Do not commit private chat contents, secrets, tokens, personal data, student data, or local machine-specific state. Skills should contain reusable instructions and safe helper scripts only.

## License

MIT
