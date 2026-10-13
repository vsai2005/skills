#!/usr/bin/env python3
"""Audit progressive-disclosure pointers in root SKILL.md files.

The audit is advisory by default. It looks for a small set of high-confidence
pointer smells rather than trying to judge prose style:
- action-only pointers that say only "Use/See/Follow <link>";
- the same progressive target linked more than once from one root;
- sentence-sized pointer clusters containing three or more progressive links.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

LOCAL_LINK_RE = re.compile(
    r"\[([^\]]+)\]\(((?:references|assets|scripts)/[^)#]+)(?:#[^)]+)?\)"
)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
ACTION_ONLY_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:use|see|follow|read|load|consult)\s+"
    r"<LINK>(?:\s*(?:,|and|or)\s*<LINK>)*\s*[:.]?\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PointerIssue:
    kind: str
    skill: str
    path: str
    line: int
    targets: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class PointerStats:
    skills: int
    pointers: int
    unique_targets: int
    vague_pointers: int
    duplicate_targets: int
    dense_clusters: int


def _segments(line: str) -> list[str]:
    return [segment.strip() for segment in SENTENCE_SPLIT_RE.split(line) if segment.strip()]


def _links(text: str) -> list[tuple[str, str]]:
    return LOCAL_LINK_RE.findall(text)


def _normalized(segment: str) -> str:
    return LOCAL_LINK_RE.sub("<LINK>", segment)


def audit_skill(skill_md: Path) -> tuple[list[PointerIssue], int, set[str]]:
    text = skill_md.read_text(encoding="utf-8")
    skill = skill_md.parent.name
    issues: list[PointerIssue] = []
    pointer_count = 0
    targets_seen: dict[str, list[int]] = {}

    for line_no, line in enumerate(text.splitlines(), start=1):
        for segment in _segments(line):
            links = _links(segment)
            if not links:
                continue

            pointer_count += len(links)
            targets = tuple(target for _label, target in links)
            for target in targets:
                targets_seen.setdefault(target, []).append(line_no)

            if ACTION_ONLY_RE.fullmatch(_normalized(segment)):
                issues.append(
                    PointerIssue(
                        kind="vague",
                        skill=skill,
                        path=skill_md.as_posix(),
                        line=line_no,
                        targets=targets,
                        message=(
                            "pointer names a progressive resource but does not say "
                            "what it is for or when to load it"
                        ),
                    )
                )

            if len(links) >= 3:
                issues.append(
                    PointerIssue(
                        kind="dense-cluster",
                        skill=skill,
                        path=skill_md.as_posix(),
                        line=line_no,
                        targets=targets,
                        message=(
                            "one sentence points to three or more progressive resources; "
                            "split branches or justify the eager cluster"
                        ),
                    )
                )

    for target, lines in sorted(targets_seen.items()):
        if len(lines) <= 1:
            continue
        issues.append(
            PointerIssue(
                kind="duplicate",
                skill=skill,
                path=skill_md.as_posix(),
                line=lines[0],
                targets=(target,),
                message=(
                    f"progressive target is linked {len(lines)} times from the root "
                    f"(lines {', '.join(str(line) for line in lines)})"
                ),
            )
        )

    return issues, pointer_count, set(targets_seen)


def audit(root: Path) -> tuple[list[PointerIssue], PointerStats]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"skills directory missing: {skills_root}")

    issues: list[PointerIssue] = []
    total_pointers = 0
    unique_targets: set[tuple[str, str]] = set()
    skills = 0

    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        skills += 1
        skill_issues, count, targets = audit_skill(skill_md)
        issues.extend(skill_issues)
        total_pointers += count
        unique_targets.update((skill_dir.name, target) for target in targets)

    stats = PointerStats(
        skills=skills,
        pointers=total_pointers,
        unique_targets=len(unique_targets),
        vague_pointers=sum(issue.kind == "vague" for issue in issues),
        duplicate_targets=sum(issue.kind == "duplicate" for issue in issues),
        dense_clusters=sum(issue.kind == "dense-cluster" for issue in issues),
    )
    return issues, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit root skill context pointers. Advisory unless --fail-on-warning is used."
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args(argv)

    try:
        issues, stats = audit(args.root.resolve())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "summary": asdict(stats),
                    "issues": [asdict(issue) for issue in issues],
                },
                indent=2,
            )
        )
    else:
        print(
            "Context pointers: "
            f"{stats.pointers} pointer(s), {stats.unique_targets} unique target(s) "
            f"across {stats.skills} skill(s)"
        )
        if issues:
            print(
                "Pointer warnings: "
                f"{stats.vague_pointers} vague, "
                f"{stats.duplicate_targets} duplicate target(s), "
                f"{stats.dense_clusters} dense cluster(s)"
            )
            for issue in issues:
                targets = ", ".join(issue.targets)
                print(
                    f"[WARN] {issue.skill}/SKILL.md:{issue.line} "
                    f"[{issue.kind}] {issue.message}: {targets}"
                )
        else:
            print("Pointer warnings: none")

    return 1 if args.fail_on_warning and issues else 0


if __name__ == "__main__":
    sys.exit(main())
