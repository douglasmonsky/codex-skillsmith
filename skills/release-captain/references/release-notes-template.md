# Release <version>

Date: <YYYY-MM-DD>
Candidate: <branch or SHA>
Base: <previous tag or deployed SHA>
Release type: <patch | minor | major | prerelease | hotfix>

## Summary

One short paragraph describing why this release exists and what changes most matter.

## User-facing changes

- <Change and user impact.>

## Fixes

- <Bug fixed and observable behavior change.>

## Breaking changes

- <Breaking change, affected users/systems, and required action.>

If none, write: None identified.

## Migration notes

- <Database, schema, storage, config, or data migration details.>

If none, write: None identified.

## Operational notes

- New or changed environment variables:
- Dependency/runtime changes:
- Infrastructure/deployment changes:
- Feature flags:
- Monitoring/logging changes:

## Validation evidence

| Check | Command | Result | Notes |
| --- | --- | --- | --- |
| Lint | `<command>` | Pass/Fail/Not run |  |
| Tests | `<command>` | Pass/Fail/Not run |  |
| Build | `<command>` | Pass/Fail/Not run |  |
| Migration check | `<command>` | Pass/Fail/Not run |  |
| Smoke test | `<command/manual check>` | Pass/Fail/Not run |  |

## Known risks

- <Risk, likelihood, impact, mitigation.>

If none, write: None identified from the inspected changes and validation results.

## Rollback plan

- Rollback trigger:
- Rollback steps:
- Data rollback or forward-fix strategy:
- Verification after rollback:

## Release checklist

- [ ] Version updated.
- [ ] Changelog/release notes reviewed.
- [ ] Tests/build passed.
- [ ] Migration plan reviewed.
- [ ] Smoke test plan ready.
- [ ] Rollback plan ready.
