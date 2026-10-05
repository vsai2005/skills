#!/usr/bin/env python3
"""Summarize Git diff scope and flag unexpectedly broad changes.

The thresholds are deliberately soft. Broad diffs can be correct; the script
exists to trigger reassessment when a narrow task spreads across the repo.
When comparing a base revision to the working tree, untracked files are included
by default so newly created code cannot evade the scope review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileChange:
    path: str
    added: int | None
    deleted: int | None
    kind: str = "tracked"

    @property
    def churn(self) -> int:
        return (self.added or 0) + (self.deleted or 0)


def parse_numstat(text: str) -> list[FileChange]:
    changes: list[FileChange] = []
    for raw in text.splitlines():
        parts = raw.split("\t", 2)
        if len(parts) != 3:
            continue
        added_raw, deleted_raw, path = parts
        added = int(added_raw) if added_raw.isdigit() else None
        deleted = int(deleted_raw) if deleted_raw.isdigit() else None
        changes.append(FileChange(path=path, added=added, deleted=deleted, kind="tracked"))
    return changes


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def untracked_change(repo: Path, rel: str) -> FileChange:
    path = repo / rel
    try:
        data = path.read_bytes()
    except OSError:
        return FileChange(path=rel, added=None, deleted=None, kind="untracked")
    if b"\x00" in data:
        return FileChange(path=rel, added=None, deleted=None, kind="untracked")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return FileChange(path=rel, added=None, deleted=None, kind="untracked")
    added = len(text.splitlines())
    return FileChange(path=rel, added=added, deleted=0, kind="untracked")


def collect_changes(repo: Path, base: str, head: str | None = None, *, include_untracked: bool = True) -> list[FileChange]:
    repo = repo.resolve()
    diff_range = f"{base}..{head}" if head else base
    tracked = parse_numstat(run_git(repo, ["diff", "--numstat", diff_range]))
    if head is not None or not include_untracked:
        return tracked

    raw = run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"])
    untracked_paths = [item for item in raw.split("\0") if item]
    return tracked + [untracked_change(repo, rel) for rel in untracked_paths]


def top_level_area(path: str) -> str:
    path = path.replace("\\", "/")
    return path.split("/", 1)[0] if "/" in path else "."


def summarize(changes: list[FileChange]) -> dict:
    areas = sorted({top_level_area(c.path) for c in changes})
    churn = sum(c.churn for c in changes)
    binary = sum(1 for c in changes if c.added is None or c.deleted is None)
    untracked = sum(1 for c in changes if c.kind == "untracked")
    signals: list[str] = []

    if len(changes) >= 20:
        signals.append("20+ files changed")
    elif len(changes) >= 10:
        signals.append("10+ files changed")

    if len(areas) >= 6:
        signals.append("6+ top-level areas touched")
    elif len(areas) >= 4:
        signals.append("4+ top-level areas touched")

    if churn >= 1500:
        signals.append("1500+ changed lines")
    elif churn >= 700:
        signals.append("700+ changed lines")

    return {
        "files_changed": len(changes),
        "untracked_files": untracked,
        "top_level_areas": areas,
        "churn": churn,
        "binary_files": binary,
        "signals": signals,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Git diff scope for change-scope review.")
    parser.add_argument("repo", nargs="?", default=".", help="Git repository path")
    parser.add_argument("--base", default="HEAD", help="Base revision for diff (default: HEAD; useful with working-tree changes)")
    parser.add_argument("--head", default=None, help="Optional head revision. Omit to compare base with working tree/index.")
    parser.add_argument("--no-untracked", action="store_true", help="Ignore untracked files when comparing against the working tree")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fail-on-signals", action="store_true", help="Exit non-zero if broad-scope signals are present")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"[ERROR] repository path is not a directory: {repo}", file=sys.stderr)
        return 2
    try:
        changes = collect_changes(repo, args.base, args.head, include_untracked=not args.no_untracked)
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    summary = summarize(changes)

    if args.json:
        print(json.dumps({"summary": summary, "files": [asdict(c) for c in changes]}, indent=2))
    else:
        print(f"Files changed: {summary['files_changed']}")
        print(f"Untracked files: {summary['untracked_files']}")
        print(f"Line churn: {summary['churn']}")
        print(f"Top-level areas: {', '.join(summary['top_level_areas']) or '(none)'}")
        if summary["signals"]:
            print("Scope review signals:")
            for signal in summary["signals"]:
                print(f"  - {signal}")
        else:
            print("Scope review signals: none")

    return 1 if args.fail_on_signals and summary["signals"] else 0


if __name__ == "__main__":
    sys.exit(main())
