#!/usr/bin/env python3
"""Generate a first-pass release notes draft from git history.

This script is dependency-free and does not mutate the repository unless
--output is supplied. The output is a starting point; Codex should inspect
material code changes and edit for accuracy before presenting release notes.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


@dataclass
class Commit:
    sha: str
    subject: str
    body: str


def run(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def infer_latest_tag() -> Optional[str]:
    proc = run(["git", "describe", "--tags", "--abbrev=0"])
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return None


def get_commits(base: Optional[str], head: str, include_merges: bool) -> List[Commit]:
    if base:
        rev_range = f"{base}..{head}"
    else:
        rev_range = head
    fmt = "%x1e%h%x1f%s%x1f%b"
    cmd = ["git", "log", f"--pretty=format:{fmt}"]
    if not include_merges:
        cmd.append("--no-merges")
    if base:
        cmd.append(rev_range)
    else:
        cmd.extend(["-20", rev_range])
    proc = run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"git log failed: {proc.stderr.strip()}")
    commits: List[Commit] = []
    for record in proc.stdout.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f", 2)
        if len(parts) < 2:
            continue
        sha = parts[0].strip()
        subject = parts[1].strip()
        body = parts[2].strip() if len(parts) > 2 else ""
        commits.append(Commit(sha, subject, body))
    return commits


def category_for(commit: Commit) -> str:
    subject = commit.subject
    body = commit.body
    lower = subject.lower()
    conventional = re.match(r"(?P<type>[a-zA-Z]+)(?:\([^)]*\))?(?P<breaking>!)?:\s*(?P<text>.+)", subject)
    if conventional:
        ctype = conventional.group("type").lower()
        if conventional.group("breaking") or "BREAKING CHANGE" in body:
            return "Breaking changes"
        if ctype == "feat":
            return "User-facing changes"
        if ctype == "fix":
            return "Fixes"
        if ctype in {"docs"}:
            return "Documentation"
        if ctype in {"perf"}:
            return "Performance"
        if ctype in {"refactor"}:
            return "Refactoring"
        if ctype in {"test", "tests"}:
            return "Tests"
        if ctype in {"build", "ci", "chore", "deps"}:
            return "Maintenance"
    if "break" in lower or "breaking" in lower:
        return "Breaking changes"
    if "fix" in lower or "bug" in lower or "hotfix" in lower:
        return "Fixes"
    if "test" in lower or "spec" in lower:
        return "Tests"
    if "doc" in lower or "readme" in lower:
        return "Documentation"
    if "depend" in lower or "bump" in lower or "upgrade" in lower:
        return "Maintenance"
    return "Other changes"


def clean_subject(subject: str) -> str:
    conventional = re.match(r"[a-zA-Z]+(?:\([^)]*\))?!?:\s*(.+)", subject)
    if conventional:
        return conventional.group(1).strip()
    return subject.strip()


def group_commits(commits: Iterable[Commit]) -> Dict[str, List[Commit]]:
    order = [
        "Breaking changes",
        "User-facing changes",
        "Fixes",
        "Performance",
        "Documentation",
        "Refactoring",
        "Tests",
        "Maintenance",
        "Other changes",
    ]
    grouped: Dict[str, List[Commit]] = {category: [] for category in order}
    for commit in commits:
        grouped[category_for(commit)].append(commit)
    return grouped


def render_markdown(version: str, base: Optional[str], head: str, commits: List[Commit]) -> str:
    grouped = group_commits(commits)
    lines: List[str] = [
        f"# Release {version}",
        "",
        f"Date: {date.today().isoformat()}",
        f"Base: {base or 'not specified; latest commits only'}",
        f"Candidate: {head}",
        "",
        "## Summary",
        "",
        "Draft generated from git history. Inspect code changes and edit this summary before release.",
        "",
    ]
    for category, items in grouped.items():
        if not items:
            continue
        lines.extend([f"## {category}", ""])
        for commit in items:
            lines.append(f"- {clean_subject(commit.subject)} (`{commit.sha}`)")
        lines.append("")
    for required in ["Migration notes", "Operational notes", "Validation evidence", "Known risks", "Rollback plan"]:
        lines.extend([f"## {required}", "", "TBD", ""])
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate release notes draft from git commits.")
    parser.add_argument("--base", help="Base tag/SHA/ref. Defaults to latest tag when available.")
    parser.add_argument("--head", default="HEAD", help="Head ref. Defaults to HEAD.")
    parser.add_argument("--version", default="<version>", help="Release version label for the notes.")
    parser.add_argument("--output", help="Optional path to write the Markdown output.")
    parser.add_argument("--include-merges", action="store_true", help="Include merge commits.")
    args = parser.parse_args(argv)

    base = args.base or infer_latest_tag()
    commits = get_commits(base, args.head, args.include_merges)
    markdown = render_markdown(args.version, base, args.head, commits)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
