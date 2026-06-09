# Release readiness checklist

Use this checklist when no repository-specific release checklist exists.

## Repository state

- [ ] Working tree contains only release-related changes.
- [ ] Current branch and target branch are identified.
- [ ] Release base is identified, usually the latest tag or the last deployed SHA.
- [ ] HEAD SHA is recorded.
- [ ] Applicable `AGENTS.md` and release docs were read.

## Versioning

- [ ] Recommended version bump is stated and justified.
- [ ] All authoritative version files agree.
- [ ] Lockfiles or generated metadata are updated when needed.
- [ ] Package/app metadata remains valid.

## Changelog and release notes

- [ ] User-facing changes are summarized.
- [ ] Fixes are summarized.
- [ ] Breaking changes are explicit.
- [ ] Migration notes are explicit.
- [ ] Operational notes are explicit.
- [ ] Known risks are listed.
- [ ] Test evidence is included.
- [ ] Rollback plan is included.

## Code and data safety

- [ ] Tests, build, and type/lint checks passed or failures are documented as blockers.
- [ ] Database/storage migrations were inspected.
- [ ] Rollback or forward-fix strategy exists for migrations.
- [ ] New environment variables are documented in example config or deployment docs.
- [ ] Dependency changes and lockfile changes are intentional.
- [ ] No secrets, credentials, tokens, private keys, or sensitive user/student data are present in release artifacts.

## Operational readiness

- [ ] Deployment path is identified.
- [ ] Smoke test checklist is ready.
- [ ] Monitoring/logs/alerts relevant to this release are identified when available.
- [ ] Rollback command or process is documented.
- [ ] Release owner or handoff target is known, if applicable.
