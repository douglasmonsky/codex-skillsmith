# Versioning policy reference

Use repository-specific versioning rules first. Use this fallback only when the repo does not define its own policy.

## SemVer fallback

Given `MAJOR.MINOR.PATCH`:

- Increment PATCH for backward-compatible bug fixes, documentation corrections, internal maintenance, or non-user-facing changes.
- Increment MINOR for backward-compatible user-facing functionality, new APIs, new CLI options, new reports, or new supported workflows.
- Increment MAJOR for breaking API behavior, incompatible schema/storage changes, removed functionality, changed default behavior that can break existing users, or required manual migration.
- Use prerelease identifiers such as `-rc.1`, `-beta.1`, or `-alpha.1` for release candidates or test distributions before a final release.

## Common authoritative version files

- JavaScript/TypeScript: `package.json`, package-lock/yarn/pnpm lockfiles, workspace package manifests.
- Python: `pyproject.toml`, `setup.cfg`, `setup.py`, package `__init__.py`, `_version.py`.
- Rust: `Cargo.toml`, `Cargo.lock`.
- Go: tags are often authoritative; inspect `go.mod` for module path rather than app version.
- Java/Kotlin: `pom.xml`, `build.gradle`, `gradle.properties`.
- .NET: `.csproj`, `Directory.Build.props`.
- Docker/Helm/Kubernetes: chart version, image tag conventions, deployment manifests.
- Mobile: iOS plist/project settings, Android Gradle versionCode/versionName.

## Version consistency checks

- All authoritative files agree on the same version.
- Generated lockfiles or manifests are updated when package metadata changes.
- Documentation examples do not mention a contradictory release version.
- CI/release workflows do not hard-code a different version.
