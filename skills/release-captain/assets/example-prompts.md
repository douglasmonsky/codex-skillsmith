# Example prompts

Use explicitly:

```text
$release-captain prepare this repo for a patch release. Draft release notes, run the relevant checks, and tell me whether it is ready.
```

```text
$release-captain cut a release candidate from this branch. Do not tag or push anything. Produce a checklist and rollback plan.
```

```text
$release-captain inspect changes since v1.4.2 and recommend the next version bump. Update release notes but do not change package versions yet.
```

```text
$release-captain this is a hotfix release. Identify only the changes since the last tag, verify the fix, and prepare a minimal rollback plan.
```
