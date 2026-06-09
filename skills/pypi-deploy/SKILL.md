---
name: pypi-deploy
description: Maintainer-only release skill for preparing, verifying, and publishing Python packages to TestPyPI or PyPI. Use when the maintainer asks to configure Trusted Publishing, prepare a Python package release, update release versions, build and check distributions, smoke-test wheels, publish to TestPyPI/PyPI, or troubleshoot PyPI release failures.
---

# PyPI Deploy

## Overview

Use this skill for maintainer release operations on Python packages. Do not use it for ordinary user installs.

Default to PyPI Trusted Publishing through GitHub Actions. Trusted Publishing avoids long-lived PyPI tokens by using GitHub Actions OIDC and publish jobs with `id-token: write`.

For repository-specific release details, read that repository's release docs and package metadata before editing release files or publishing.

If asked to create or repair a publish workflow, use the project-specific release gate and adapt it to the repository's real package layout. Do not paste a generic workflow without checking the repo.

## Core Rules

- Do not request, print, store, commit, or echo PyPI/TestPyPI API tokens.
- Do not create `.pypirc`.
- Do not add token-based GitHub secrets unless the maintainer explicitly approves a fallback.
- Do not publish to TestPyPI or PyPI unless the maintainer explicitly asks for that action.
- Do not publish from the local machine when the repository has a GitHub Actions Trusted Publishing workflow.
- Do not publish on ordinary `push` or `pull_request` events.
- Gate publishing by `workflow_dispatch` or GitHub Release publication, preferably with protected GitHub environments.
- Treat package versions as immutable after upload. If a bad file/version reaches PyPI or TestPyPI, prepare a new patch version.
- Keep release artifacts synthetic and clean. Never include real logs, generated dashboards with real data, SQLite databases, CSV exports, support bundles, secrets, or raw context.
- Do not push release branches, tags, or production publish workflows until the maintainer approves.

## Setup Review

Before changing release tooling:

1. Inspect the repo state with `git status --short --branch`.
2. Identify the distribution name, import package, console scripts, package data, build backend, and release workflow paths.
3. Read release-critical files such as:
   - `pyproject.toml`
   - package `__init__.py`
   - `README.md`
   - `CHANGELOG.md`
   - `MANIFEST.in`
   - `.github/workflows/*.yml`
   - release or packaging scripts
   - docs covering install, privacy, security, CLI, and development
4. Check whether PyPI/TestPyPI Trusted Publishers are already configured or need maintainer setup.

## Trusted Publishing Model

Prefer a GitHub Actions workflow that:

- builds distributions once
- uploads the built files as workflow artifacts
- publishes those same artifacts to TestPyPI or PyPI in separate jobs
- grants `contents: read` to build jobs
- grants `id-token: write` only to publish jobs
- uses `pypa/gh-action-pypi-publish@release/v1`
- uses `repository-url: https://test.pypi.org/legacy/` for TestPyPI
- avoids username, password, and API token fields
- runs production PyPI publishing only on GitHub Release publication or explicit maintainer-dispatched target

For new Trusted Publisher setup, tell the maintainer the exact values to configure:

- PyPI project/distribution name
- GitHub owner
- GitHub repository
- workflow filename
- GitHub environment name, if used

## Version Update Procedure

When the maintainer asks for a release version update:

1. Update every authoritative version field used by the project.
2. Update tests or docs that assert the version.
3. Convert `## Unreleased` into a dated release section while preserving a fresh `## Unreleased` heading.
4. Run the repository's release checker if present.
5. Do not tag or push until approval.

## Local Release Gate

Find the repository's real validation commands before inventing new ones. A complete gate usually includes:

- formatter/linter checks
- type checks
- unit tests
- coverage when configured
- `python -m compileall`
- frontend or bundled asset syntax checks when package data includes JavaScript
- release-readiness scripts
- `git diff --check`
- clean build from a removed `dist/`, `build/`, and egg-info state
- `python -m build`
- `python -m twine check dist/*`
- wheel and sdist content inspection
- SHA256 hashes for built distributions
- clean temporary virtualenv wheel smoke test

If `twine` or `build` is missing, install only the needed build tooling in the active development environment after checking the project's dependency policy.

## Smoke Testing

Before publishing:

- Install the wheel in a clean temporary virtual environment.
- Run `--version`, `--help`, and important subcommand help.
- Exercise safe initialization commands with temporary output paths.
- Verify imports and package data are present.
- For TestPyPI, use `--no-deps` when dependency availability on TestPyPI is unreliable.

After production PyPI publishing:

- Prefer `pipx install <distribution>==<version>` for CLI packages.
- Verify the installed command reports the expected version and core help commands work.

## Publishing Procedure

For TestPyPI:

1. Confirm release files are committed locally.
2. Confirm the maintainer has approved pushing the branch/tag or running the workflow.
3. Run the GitHub Actions publish workflow manually with target `testpypi`.
4. Smoke-test installation from TestPyPI.
5. Report results before proceeding.

For PyPI:

1. Require explicit maintainer approval after TestPyPI succeeds, unless the maintainer explicitly chose to skip TestPyPI.
2. Publish by GitHub Release publication or manual workflow target `pypi`.
3. Smoke-test from PyPI.
4. Report final package names, versions, dist hashes, and remaining risks.

## Troubleshooting

If publish fails because the project is unknown:

- confirm the pending Trusted Publisher exists on the correct PyPI service
- confirm the project/distribution name exactly matches the package metadata
- confirm the GitHub owner, repository, workflow filename, and environment match the PyPI configuration
- confirm the publish job has `permissions: id-token: write`

If the upload partially succeeds:

- do not retry the same version blindly
- inspect which files were accepted
- if the version is burned, prepare a patch release

If the distribution name looks wrong:

- distinguish PyPI distribution name, import package name, CLI command name, and repository name
- update install docs to use the distribution name, not necessarily the command or repo name

## Final Report

After release work, report:

- files changed
- version fields updated
- PyPI distribution name
- import package name
- CLI command name
- local release gate status
- dist filenames and SHA256 hashes
- wheel/sdist content verification
- TestPyPI publish and install status
- PyPI publish and install status
- skipped checks, risks, and follow-up issues
