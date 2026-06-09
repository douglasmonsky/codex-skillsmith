#!/usr/bin/env python3
"""Release readiness audit helper.

This script is intentionally dependency-free. It gathers repository state and
release risk signals that a Codex release-captain skill can use as evidence.
It does not mutate the repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


@dataclass
class CommandResult:
    command: str
    ok: bool
    stdout: str
    stderr: str


@dataclass
class VersionFile:
    path: str
    kind: str
    version: Optional[str]


@dataclass
class Audit:
    cwd: str
    is_git_repo: bool
    branch: Optional[str]
    upstream: Optional[str]
    head_sha: Optional[str]
    latest_tag: Optional[str]
    base_ref: Optional[str]
    working_tree_dirty: bool
    uncommitted_files: List[str]
    changed_files: List[str]
    recent_commits: List[str]
    package_managers: List[str]
    version_files: List[VersionFile]
    ci_files: List[str]
    release_docs: List[str]
    migration_files: List[str]
    dependency_files_changed: List[str]
    config_files_changed: List[str]
    test_files_changed: List[str]
    risk_signals: List[str]
    commands: List[CommandResult]


def run(cmd: Sequence[str], timeout: int = 15) -> CommandResult:
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return CommandResult(" ".join(cmd), proc.returncode == 0, proc.stdout.rstrip("\n"), proc.stderr.rstrip("\n"))
    except Exception as exc:  # pragma: no cover - defensive helper
        return CommandResult(" ".join(cmd), False, "", f"{type(exc).__name__}: {exc}")


def git(args: Sequence[str], commands: List[CommandResult], timeout: int = 15) -> CommandResult:
    result = run(["git", *args], timeout=timeout)
    commands.append(result)
    return result


def split_lines(value: str) -> List[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def parse_status_paths(value: str) -> List[str]:
    paths: List[str] = []
    for raw_line in value.splitlines():
        if not raw_line:
            continue
        path = raw_line[3:] if len(raw_line) > 3 else raw_line
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        paths.append(path.strip())
    return paths


def first_existing(paths: Iterable[str]) -> List[str]:
    return [p for p in paths if Path(p).exists()]


def glob_existing(patterns: Iterable[str]) -> List[str]:
    found: List[str] = []
    for pattern in patterns:
        for path in Path.cwd().glob(pattern):
            if path.is_file():
                found.append(str(path.as_posix()))
    return sorted(set(found))


def read_text(path: Path, max_bytes: int = 200_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def detect_version_files() -> List[VersionFile]:
    version_files: List[VersionFile] = []

    package_json = Path("package.json")
    if package_json.exists():
        try:
            data = json.loads(read_text(package_json))
            version_files.append(VersionFile("package.json", "npm", data.get("version")))
        except json.JSONDecodeError:
            version_files.append(VersionFile("package.json", "npm", None))

    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        text = read_text(pyproject)
        match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', text)
        version_files.append(VersionFile("pyproject.toml", "python", match.group(1) if match else None))

    setup_cfg = Path("setup.cfg")
    if setup_cfg.exists():
        text = read_text(setup_cfg)
        match = re.search(r'(?m)^version\s*=\s*([^\s#]+)', text)
        version_files.append(VersionFile("setup.cfg", "python", match.group(1) if match else None))

    cargo = Path("Cargo.toml")
    if cargo.exists():
        text = read_text(cargo)
        match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', text)
        version_files.append(VersionFile("Cargo.toml", "rust", match.group(1) if match else None))

    pom = Path("pom.xml")
    if pom.exists():
        text = read_text(pom)
        match = re.search(r"<version>([^<]+)</version>", text)
        version_files.append(VersionFile("pom.xml", "maven", match.group(1) if match else None))

    gradle_props = Path("gradle.properties")
    if gradle_props.exists():
        text = read_text(gradle_props)
        match = re.search(r'(?m)^(?:version|VERSION_NAME)\s*=\s*([^\s#]+)', text)
        version_files.append(VersionFile("gradle.properties", "gradle", match.group(1) if match else None))

    dotnet_files = sorted(Path.cwd().glob("*.csproj")) + sorted(Path.cwd().glob("**/*.csproj"))[:20]
    for csproj in dotnet_files[:20]:
        text = read_text(csproj)
        match = re.search(r"<(?:Version|AssemblyVersion|FileVersion)>([^<]+)</", text)
        if match:
            version_files.append(VersionFile(csproj.as_posix(), ".net", match.group(1)))

    version_plain = Path("VERSION")
    if version_plain.exists():
        version_files.append(VersionFile("VERSION", "plain", read_text(version_plain).splitlines()[0].strip() or None))

    return version_files


def detect_package_managers() -> List[str]:
    signals = {
        "npm": ["package-lock.json"],
        "yarn": ["yarn.lock"],
        "pnpm": ["pnpm-lock.yaml"],
        "bun": ["bun.lock", "bun.lockb"],
        "python/uv": ["uv.lock"],
        "python/poetry": ["poetry.lock"],
        "python/pip": ["requirements.txt"],
        "rust/cargo": ["Cargo.lock"],
        "go": ["go.mod", "go.sum"],
        "java/maven": ["pom.xml"],
        "java/gradle": ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"],
        ".net": ["*.csproj", "*.sln"],
    }
    detected: List[str] = []
    for name, patterns in signals.items():
        for pattern in patterns:
            if list(Path.cwd().glob(pattern)):
                detected.append(name)
                break
    return detected


def classify_changed_files(changed_files: List[str]) -> dict:
    dep_names = {
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lock",
        "bun.lockb",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "poetry.lock",
        "uv.lock",
        "Cargo.toml",
        "Cargo.lock",
        "go.mod",
        "go.sum",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "gradle.properties",
    }
    dep = [f for f in changed_files if Path(f).name in dep_names]
    config = [
        f
        for f in changed_files
        if re.search(r"(^|/)(\.env|env\.example|config|settings|helm|k8s|kubernetes|Dockerfile|docker-compose|\.github/workflows)", f, re.I)
        or Path(f).suffix in {".yaml", ".yml", ".toml", ".ini"} and "test" not in f.lower()
    ]
    migrations = [f for f in changed_files if re.search(r"(^|/)(migrations?|db|schema|prisma|alembic|liquibase|flyway)(/|$)", f, re.I)]
    tests = [f for f in changed_files if re.search(r"(^|/)(test|tests|spec|__tests__)(/|$)|(_test|\.test|\.spec)\.", f, re.I)]
    return {"dependency": dep, "config": config, "migrations": migrations, "tests": tests}


def infer_risk_signals(
    *,
    dirty: bool,
    changed_files: List[str],
    uncommitted_files: List[str],
    classified: dict,
    version_files: List[VersionFile],
    release_docs: List[str],
) -> List[str]:
    risks: List[str] = []
    if dirty:
        risks.append("Working tree has uncommitted changes; confirm they are release-related before tagging or publishing.")
    if classified["migrations"]:
        risks.append("Database/schema/storage migration files changed; release notes need migration and rollback/forward-fix details.")
    if classified["dependency"]:
        risks.append("Dependency or lock files changed; verify lockfiles and dependency compatibility.")
    if classified["config"]:
        risks.append("Config, deployment, environment, or workflow files changed; document operational impact and smoke tests.")
    if not classified["tests"] and changed_files:
        risks.append("No changed test files detected in this diff; verify existing coverage is sufficient.")
    versions = [vf.version for vf in version_files if vf.version]
    if len(set(versions)) > 1:
        risks.append("Multiple version files contain different versions; reconcile before release.")
    if not release_docs:
        risks.append("No obvious release documentation found; use the skill fallback checklist and templates.")
    sensitive_patterns = [
        r"secret",
        r"token",
        r"private[_-]?key",
        r"credential",
        r"password",
        r"student",
        r"pii",
    ]
    for f in changed_files + uncommitted_files:
        lowered = f.lower()
        if any(re.search(pattern, lowered) for pattern in sensitive_patterns):
            risks.append(f"Potentially sensitive file path changed: {f}. Inspect before release artifact creation.")
            break
    return risks


def build_audit(base_ref: Optional[str]) -> Audit:
    commands: List[CommandResult] = []
    cwd = os.getcwd()

    is_repo_result = git(["rev-parse", "--is-inside-work-tree"], commands)
    is_git_repo = is_repo_result.ok and is_repo_result.stdout == "true"
    if not is_git_repo:
        return Audit(
            cwd=cwd,
            is_git_repo=False,
            branch=None,
            upstream=None,
            head_sha=None,
            latest_tag=None,
            base_ref=base_ref,
            working_tree_dirty=False,
            uncommitted_files=[],
            changed_files=[],
            recent_commits=[],
            package_managers=detect_package_managers(),
            version_files=detect_version_files(),
            ci_files=glob_existing([".github/workflows/*", ".gitlab-ci.yml", "circle.yml", ".circleci/*", "azure-pipelines.yml"]),
            release_docs=glob_existing(["CHANGELOG*", "RELEASE*", "docs/**/release*", "docs/**/deploy*", "README*", "CONTRIBUTING*"]),
            migration_files=[],
            dependency_files_changed=[],
            config_files_changed=[],
            test_files_changed=[],
            risk_signals=["Current directory is not inside a git repository; release diff and tag evidence unavailable."],
            commands=commands,
        )

    branch_result = git(["branch", "--show-current"], commands)
    head_result = git(["rev-parse", "--short=12", "HEAD"], commands)
    upstream_result = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], commands)
    tag_result = git(["describe", "--tags", "--abbrev=0"], commands)
    status_result = git(["status", "--porcelain"], commands)

    latest_tag = tag_result.stdout if tag_result.ok and tag_result.stdout else None
    base = base_ref or latest_tag

    if base:
        changed_result = git(["diff", "--name-only", f"{base}...HEAD"], commands, timeout=30)
        commits_result = git(["log", "--oneline", "--decorate=no", f"{base}..HEAD"], commands, timeout=30)
    else:
        changed_result = git(["diff", "--name-only", "HEAD~20...HEAD"], commands, timeout=30)
        if not changed_result.ok:
            changed_result = git(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], commands, timeout=30)
        commits_result = git(["log", "--oneline", "--decorate=no", "-20"], commands, timeout=30)

    changed_files = split_lines(changed_result.stdout) if changed_result.ok else []
    recent_commits = split_lines(commits_result.stdout) if commits_result.ok else []
    uncommitted_files = parse_status_paths(status_result.stdout)
    classified = classify_changed_files(changed_files)

    ci_files = glob_existing([".github/workflows/*", ".gitlab-ci.yml", "circle.yml", ".circleci/*", "azure-pipelines.yml", "Jenkinsfile"])
    release_docs = glob_existing(["CHANGELOG*", "RELEASE*", "docs/**/release*", "docs/**/deploy*", "README*", "CONTRIBUTING*"])
    version_files = detect_version_files()

    risks = infer_risk_signals(
        dirty=bool(status_result.stdout),
        changed_files=changed_files,
        uncommitted_files=uncommitted_files,
        classified=classified,
        version_files=version_files,
        release_docs=release_docs,
    )

    return Audit(
        cwd=cwd,
        is_git_repo=True,
        branch=branch_result.stdout or None,
        upstream=upstream_result.stdout if upstream_result.ok else None,
        head_sha=head_result.stdout if head_result.ok else None,
        latest_tag=latest_tag,
        base_ref=base,
        working_tree_dirty=bool(status_result.stdout),
        uncommitted_files=uncommitted_files,
        changed_files=changed_files,
        recent_commits=recent_commits,
        package_managers=detect_package_managers(),
        version_files=version_files,
        ci_files=ci_files,
        release_docs=release_docs,
        migration_files=classified["migrations"],
        dependency_files_changed=classified["dependency"],
        config_files_changed=classified["config"],
        test_files_changed=classified["tests"],
        risk_signals=risks,
        commands=commands,
    )


def emit_markdown(audit: Audit) -> str:
    version_lines = [f"- `{vf.path}` ({vf.kind}): {vf.version or 'version not detected'}" for vf in audit.version_files]
    command_lines = [
        f"- `{' '.join(cr.command.split())}`: {'ok' if cr.ok else 'failed'}"
        + (f" — {cr.stderr[:160]}" if not cr.ok and cr.stderr else "")
        for cr in audit.commands
    ]

    def section_list(items: List[str], empty: str = "None detected.") -> str:
        return "\n".join(f"- `{item}`" for item in items) if items else empty

    return f"""# Release audit

## Repository state

- CWD: `{audit.cwd}`
- Git repository: {'yes' if audit.is_git_repo else 'no'}
- Branch: `{audit.branch or 'unknown'}`
- Upstream: `{audit.upstream or 'none detected'}`
- HEAD: `{audit.head_sha or 'unknown'}`
- Latest tag: `{audit.latest_tag or 'none detected'}`
- Base ref: `{audit.base_ref or 'none detected'}`
- Working tree dirty: {'yes' if audit.working_tree_dirty else 'no'}

## Package and version signals

Package managers: {', '.join(audit.package_managers) if audit.package_managers else 'none detected'}

{chr(10).join(version_lines) if version_lines else 'No common version files detected.'}

## Changed files since base

{section_list(audit.changed_files)}

## Recent commits since base

{section_list(audit.recent_commits, 'None detected or base unavailable.')}

## Uncommitted files

{section_list(audit.uncommitted_files)}

## Release docs and CI

Release docs:
{section_list(audit.release_docs)}

CI files:
{section_list(audit.ci_files)}

## Risk signals

{chr(10).join(f'- {risk}' for risk in audit.risk_signals) if audit.risk_signals else 'No automatic risk signals detected. Still verify tests, build, release notes, smoke tests, and rollback plan.'}

## Classified release-sensitive changes

Migrations:
{section_list(audit.migration_files)}

Dependency files:
{section_list(audit.dependency_files_changed)}

Config/deployment files:
{section_list(audit.config_files_changed)}

Test files:
{section_list(audit.test_files_changed)}

## Audit commands

{chr(10).join(command_lines)}
""".strip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit repository state for release preparation.")
    parser.add_argument("--base", dest="base_ref", help="Base ref/tag/SHA for release diff. Defaults to latest tag when available.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args(argv)

    audit = build_audit(args.base_ref)
    if args.json:
        print(json.dumps(asdict(audit), indent=2, sort_keys=True))
    else:
        print(emit_markdown(audit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
