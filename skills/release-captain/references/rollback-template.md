# Rollback plan template

## Rollback trigger conditions

Rollback or halt rollout if any of these occur:

- Error rate, latency, job failures, or support tickets exceed the agreed threshold.
- Login, checkout, grading, data import, report generation, or another critical path fails smoke testing.
- Migration causes data loss, corruption, or incompatible reads/writes.
- Security, privacy, or permissions behavior differs from expected behavior.

## Pre-rollback facts to capture

- Release version/tag/SHA:
- Deployment environment:
- Deployment start time:
- First observed issue time:
- Error/log/dashboard links, if available:
- Data migration status:

## Rollback steps

1. Stop or pause rollout if staged rollout is available.
2. Revert deployment to the previous known-good version/tag/SHA.
3. If database/storage changes were applied, follow the migration-specific rollback or forward-fix instructions.
4. Clear or refresh caches only if the release notes identify cache incompatibility.
5. Restart affected jobs/workers/services only if required by the deployment platform.
6. Verify the critical path with smoke tests.
7. Record the final production SHA/version and remaining risks.

## Data migration strategy

Choose one:

- Reversible migration: run the down migration and verify reads/writes.
- Forward-only migration: deploy a compatibility fix or forward-fix migration.
- Dual-read/write migration: disable new writes, restore previous behavior, and verify both old and new data paths.
- Manual intervention required: list owner, script, backup source, and verification query.

## Post-rollback verification

- [ ] Application starts successfully.
- [ ] Critical path smoke test passes.
- [ ] Error rate returns to baseline.
- [ ] Background jobs/workers are healthy.
- [ ] Data integrity checks pass.
- [ ] Release notes or incident notes are updated.
