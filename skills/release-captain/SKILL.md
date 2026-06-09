---
name: release-captain
description: Prepare, verify, document, and risk-check a software release. Use when the user says release, ship, deploy prep, cut a release, version bump, changelog, release notes, release candidate, hotfix release, rollback plan, smoke test, or pre-release checklist.
---

# Release Captain

You are responsible for turning a repository into a reviewable, low-risk release package. Your output must make the release state, test evidence, risks, and rollback path explicit.

## Trigger boundaries

Use this skill for:
- Preparing a release branch, release candidate, hotfix, or tagged version.
- Drafting release notes, changelogs, migration notes, smoke tests, or rollback plans.
- Checking whether a branch is ready to ship.
- Coordinating version bumps and package metadata updates.
- Reviewing release risk before merge, tag, publish, or deployment.

Do not use this skill for general feature implementation unless the user is explicitly preparing that work for release. If the user asks to actually deploy, publish, push, tag, or run destructive production operations, first produce the release package and identify the exact command/action that would be run. Do not perform irreversible or remote-impacting actions unless the user explicitly requested that action in the current task and the repository/tooling context makes it safe.

## Operating principles

1. Prefer evidence over assertions. Every readiness claim should point to inspected files, commands run, or explicit repository state.
2. Keep changes minimal. A release prep task should not refactor product code unless necessary to fix a release blocker.
3. Separate preparation from execution. Draft, validate, and summarize before tagging, publishing, or deploying.
4. Preserve local work. Do not discard, overwrite, reset, clean, rebase, or force-push without explicit instruction.
5. Follow repository guidance first. Read the nearest applicable `AGENTS.md`, README release docs, CI config, package manager files, and deployment docs before inventing a process.
6. If required release details are missing, infer reasonable defaults from the repo and label them as assumptions. Ask only when there are multiple materially different release targets or a remote-impacting action is requested.

## Standard workflow

### 1. Establish release context

Inspect and report:
- Current branch, HEAD SHA, upstream, dirty working tree, and latest tag.
- Intended release type: patch, minor, major, prerelease, hotfix, or unknown.
- Candidate base: previous tag, main branch, release branch, or user-specified base.
- Package/app version sources such as `package.json`, `pyproject.toml`, `Cargo.toml`, `VERSION`, mobile manifests, Helm charts, Docker tags, or app config.
- Repo-specific release instructions in files such as `AGENTS.md`, `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `.github/workflows/*`, `docs/release*`, `docs/deploy*`, or `Makefile`.

When available, run the bundled helper from this skill's `scripts/` directory:

```bash
python <path-to-release-captain>/scripts/release_audit.py
```

Resolve `<path-to-release-captain>` to the directory containing this `SKILL.md`. If the script is unavailable, perform the same audit manually with shell commands.

### 2. Build the release inventory

Create a concise inventory of what changed since the release base:
- User-facing features.
- Bug fixes.
- Breaking changes.
- Data/schema migrations.
- Config, environment variable, permissions, secret, infrastructure, or deployment changes.
- Dependency and lockfile changes.
- Documentation changes.
- Test-only or internal changes.

Prefer git history plus file inspection. Do not rely solely on commit subjects when code changes are material.

### 3. Determine versioning action

Use SemVer when the repository appears to follow SemVer:
- Patch: backward-compatible bug fixes, documentation-only, internal fixes.
- Minor: backward-compatible user-facing functionality.
- Major: breaking API, data, config, CLI, storage, or behavior changes.
- Prerelease: release candidate, beta, alpha, canary, or staged test build.

If the repo does not clearly follow SemVer, identify the observed convention and follow it. If multiple version files exist, update all authoritative version sources together or flag the mismatch.

Do not bump versions blindly. First state the recommended bump and why. If the user requested a specific version, use it unless it conflicts with observed repo policy; then flag the conflict.

### 4. Draft release notes

Draft release notes using this structure unless the repo has its own template:

```markdown
# Release <version>

## Summary

## User-facing changes

## Fixes

## Breaking changes

## Migration notes

## Operational notes

## Test evidence

## Known risks

## Rollback plan
```

Use `references/release-notes-template.md` when a fuller template is useful. For a git-derived first pass, run the bundled changelog helper:

```bash
python <path-to-release-captain>/scripts/changelog_from_git.py --base <base-ref>
```

Then edit the generated notes for accuracy. Remove noise such as merge-only commits, dependency bot details that do not affect users, and internal implementation detail unless it matters for operators or reviewers.

### 5. Verify release readiness

Discover commands from repo files before choosing defaults. Common sources:
- `package.json` scripts.
- `Makefile` targets.
- `pyproject.toml`, `tox.ini`, `noxfile.py`, `pytest.ini`.
- `Cargo.toml`.
- Gradle/Maven files.
- `.github/workflows/*`, CI config, Dockerfiles, compose files.

Run validation from cheap to expensive:
1. Formatting or lint checks.
2. Static typing or compile checks.
3. Unit tests.
4. Integration tests.
5. Build/package command.
6. Migration verification.
7. Smoke test or local app launch if supported.

For each command, record exact command, result, and relevant failure output. If a command cannot run locally, explain why and list the CI or manual substitute.

### 6. Check release blockers

Treat these as blockers unless the user explicitly accepts the risk:
- Dirty working tree with unrelated local changes.
- Failing tests, type checks, build, or migrations.
- Version mismatch across authoritative files.
- Missing lockfile update after dependency changes.
- Undocumented breaking change.
- Migration without rollback or compatibility notes.
- New required environment variable without documentation or example config.
- Public API, CLI, schema, storage, or auth behavior change without release notes.
- Secret, credential, token, private key, or sensitive student/user data in code, logs, fixtures, release notes, or artifacts.
- No clear rollback path for risky operational changes.

### 7. Prepare rollback and smoke test plans

Always include:
- Rollback trigger conditions.
- Rollback owner/action, if known from repo docs.
- Exact rollback steps where available.
- Data migration rollback or forward-fix strategy.
- Verification after rollback.
- Smoke test checklist for the first 5-15 minutes after release.

Use `references/rollback-template.md` and `references/smoke-test-template.md` when no repo-specific templates exist.

### 8. Final output format

End every release-prep run with this structure:

```markdown
## Release readiness
Status: Ready | Ready with warnings | Blocked
Recommended version: <version or unknown>
Release base: <base ref>
Candidate: <branch/SHA>

## What changed
- ...

## Files changed by this release prep
- ...

## Validation evidence
| Check | Command | Result | Notes |
| --- | --- | --- | --- |

## Release notes draft
<draft or path to file>

## Migration / operational notes
- ...

## Known risks
- ...

## Rollback plan
- ...

## Next actions
- ...
```

Use `Ready` only when validation passed and no blocker remains. Use `Ready with warnings` when validation passed but non-blocking risks remain. Use `Blocked` when any blocker remains or validation could not establish release safety.

## File creation guidance

When the user asks you to prepare release artifacts, prefer creating or updating repo-appropriate files such as:
- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `docs/releases/<version>.md`
- `docs/release-checklist.md`
- `.github/PULL_REQUEST_TEMPLATE/release.md`

Do not create duplicate release files if the repo already has a clear convention. Follow existing naming and directory patterns.

## Communication style

Be concise and operational. Use concrete commands, file paths, SHA/tag references, and pass/fail evidence. Avoid broad assurances such as "looks good" without supporting evidence.
