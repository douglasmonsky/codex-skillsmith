# Smoke test template

Use this for the first verification pass after a release candidate build or deployment.

## Setup

- Environment:
- Version/tag/SHA:
- Test account or fixture:
- Feature flags:
- Known limitations:

## Critical path checks

- [ ] Application loads without console/server errors.
- [ ] Authentication or main entry flow works.
- [ ] Primary create/update/read/delete flow works, if applicable.
- [ ] Main data import/export or report generation flow works, if applicable.
- [ ] Permissions/roles behave correctly for at least one allowed and one denied action.
- [ ] Background jobs, queues, or scheduled tasks are healthy, if applicable.
- [ ] Error logging/monitoring shows no new high-severity issue.

## Release-specific checks

- [ ] <Feature/fix from this release> behaves as expected.
- [ ] <Migration/config/dependency change> behaves as expected.
- [ ] <Regression-prone area> still works.

## Pass/fail record

| Check | Result | Evidence/notes |
| --- | --- | --- |
| Application load |  |  |
| Critical path |  |  |
| Release-specific behavior |  |  |
| Monitoring/logs |  |  |
