#!/usr/bin/env python3
"""Check or refresh OpenAI skill metadata freshness against discovery descriptions."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
HASH_RE = re.compile(r"^# source-description-sha256: ([0-9a-f]{64})$", re.MULTILINE)


def skill_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"missing frontmatter: {skill_md}")
    for raw in match.group(1).splitlines():
        if raw.startswith("description:"):
            value = raw.split(":", 1)[1].strip()
            if value.startswith(('"', "'")) and value.endswith(value[0]) and len(value) >= 2:
                value = value[1:-1]
            if value:
                return value
    raise ValueError(f"missing description: {skill_md}")


def description_sha256(skill_md: Path) -> str:
    return hashlib.sha256(skill_description(skill_md).encode("utf-8")).hexdigest()


def check_skill(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        return f"{skill_dir.name}: agents/openai.yaml missing"
    text = openai_yaml.read_text(encoding="utf-8")
    match = HASH_RE.search(text)
    expected = description_sha256(skill_md)
    if not match:
        return f"{skill_dir.name}: source-description-sha256 missing"
    if match.group(1) != expected:
        return f"{skill_dir.name}: OpenAI metadata is stale ({match.group(1)} != {expected})"
    return None


def refresh_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    text = openai_yaml.read_text(encoding="utf-8")
    line = f"# source-description-sha256: {description_sha256(skill_md)}"
    if HASH_RE.search(text):
        text = HASH_RE.sub(line, text, count=1)
    else:
        text = line + "\n" + text
    openai_yaml.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or refresh OpenAI skill metadata freshness.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--write", action="store_true", help="Refresh description hashes in agents/openai.yaml")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    skill_dirs = sorted(
        path for path in (root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if args.write:
        for skill_dir in skill_dirs:
            refresh_skill(skill_dir)
        print(f"[OK] Refreshed OpenAI metadata hashes for {len(skill_dirs)} skill(s)")
        return 0

    problems = [problem for skill_dir in skill_dirs if (problem := check_skill(skill_dir))]
    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}", file=sys.stderr)
        return 1
    print(f"[OK] OpenAI metadata is current for {len(skill_dirs)} skill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
