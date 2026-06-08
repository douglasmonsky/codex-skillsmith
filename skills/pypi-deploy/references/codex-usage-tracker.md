# codex-usage-tracker Release Profile

Use this reference for `douglasmonsky/codex-usage-tracker`.

## Names

```text
GitHub repository: douglasmonsky/codex-usage-tracker
PyPI/TestPyPI distribution: codex-usage-tracking
Python import package: codex_usage_tracker
Console command: codex-usage-tracker
Publish workflow filename: publish.yml
TestPyPI environment: testpypi
PyPI environment: pypi
```

The PyPI distribution name is not `codex-usage-tracker`.

Install docs should say:

```bash
pipx install codex-usage-tracking
codex-usage-tracker setup
codex-usage-tracker serve-dashboard --open
```

## Trusted Publisher Configuration

For TestPyPI:

```text
Project name: codex-usage-tracking
Owner: douglasmonsky
Repository: codex-usage-tracker
Workflow filename: publish.yml
Environment: testpypi
```

For PyPI:

```text
Project name: codex-usage-tracking
Owner: douglasmonsky
Repository: codex-usage-tracker
Workflow filename: publish.yml
Environment: pypi
```

## Release-Critical Files

Read these before preparing a release:

```text
README.md
CHANGELOG.md
pyproject.toml
src/codex_usage_tracker/__init__.py
.codex-plugin/plugin.json
MANIFEST.in
scripts/check_release.py
docs/development.md
docs/architecture.md
docs/privacy.md
docs/install.md
docs/cli-reference.md
docs/cli-json-schemas.md
SECURITY.md
.github/workflows/ci.yml
.github/workflows/publish.yml
```

## Naming Checks

Verify:

- `[project].name = "codex-usage-tracking"`
- package version matches the target release
- import package remains `codex_usage_tracker`
- console script remains `codex-usage-tracker`
- PyPI/TestPyPI URLs point to `codex-usage-tracking`

## Version Update Files

Update version fields in:

```text
pyproject.toml
src/codex_usage_tracker/__init__.py
.codex-plugin/plugin.json
```

Update tests or docs that assert the version.

## Local Release Gate

Run the repository's configured checks first. The full known gate is:

```bash
python -m ruff check .
python -m mypy
python -m pytest
python -m pytest --cov=codex_usage_tracker --cov-report=term-missing
python -m compileall src
node --check src/codex_usage_tracker/plugin_data/dashboard/dashboard_format.js
node --check src/codex_usage_tracker/plugin_data/dashboard/dashboard_data.js
node --check src/codex_usage_tracker/plugin_data/dashboard/dashboard.js
node --check src/codex_usage_tracker/plugin_data/dashboard/dashboard_state.js
python scripts/check_release.py
git diff --check
rm -rf dist build *.egg-info src/*.egg-info
python -m build
python -m twine check dist/*
python scripts/check_release.py --dist
```

If `twine` is missing:

```bash
python -m pip install --upgrade twine
```

## Wheel Smoke Test

Replace `$VERSION` with the target version.

```bash
python -m venv /tmp/codex-usage-tracking-smoke
. /tmp/codex-usage-tracking-smoke/bin/activate
python -m pip install --upgrade pip
python -m pip install "dist/codex_usage_tracking-$VERSION-py3-none-any.whl"
codex-usage-tracker --version
codex-usage-tracker --help
codex-usage-tracker doctor --json
codex-usage-tracker dashboard --help
codex-usage-tracker serve-dashboard --help
codex-usage-tracker init-pricing --output /tmp/codex-usage-pricing.json --force
codex-usage-tracker init-allowance --output /tmp/codex-usage-allowance.json --force
codex-usage-tracker init-thresholds --output /tmp/codex-usage-thresholds.json --force
codex-usage-tracker init-projects --output /tmp/codex-usage-projects.json --force
deactivate
```

Also smoke-test plugin installation into temporary paths:

```bash
codex-usage-tracker install-plugin \
  --plugin-dir /tmp/codex-usage-tracker-plugin-smoke \
  --marketplace /tmp/codex-usage-marketplace-smoke.json \
  --force
```

## TestPyPI Install Test

After a TestPyPI publish succeeds:

```bash
python -m venv /tmp/codex-usage-testpypi
. /tmp/codex-usage-testpypi/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps "codex-usage-tracking==$VERSION"
codex-usage-tracker --version
python -c "import codex_usage_tracker; print(codex_usage_tracker.__version__)"
deactivate
```

Use `--no-deps` because TestPyPI may not have all dependencies.

## PyPI Install Test

After production PyPI publish succeeds:

```bash
pipx install "codex-usage-tracking==$VERSION"
codex-usage-tracker --version
codex-usage-tracker setup --help
codex-usage-tracker serve-dashboard --help
```

## MCP Runtime Pinning

The MCP runtime launcher must not track `main`.

If the runtime launcher installs from GitHub:

- pin to a 40-character release commit SHA
- do not use `codex-usage-tracker.git@main`

If the runtime launcher installs from PyPI:

- use `codex-usage-tracking==$VERSION`
- do not use the old distribution name

When changing runtime launcher files, update both the source skill copy and packaged skill copy if the repo uses mirrored packaged skill assets.

## Preferred Commit Sequence

Do not push until maintainer approval.

```bash
git checkout -b release/$VERSION

# Make release edits except final runtime pin.
python scripts/check_release.py
git add .
git commit -m "Prepare $VERSION release"

RELEASE_SOURCE_SHA="$(git rev-parse HEAD)"

# Update MCP runtime pin to RELEASE_SOURCE_SHA or codex-usage-tracking==$VERSION.
python scripts/check_release.py
git add .
git commit -m "Pin MCP runtime package for $VERSION"

git tag -a "v$VERSION" -m "codex-usage-tracker $VERSION"
```
