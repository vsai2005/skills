#!/usr/bin/env python3
"""Copy selected skills to an Agent Skills directory.

The destination is explicit so this helper remains harness-neutral. Examples:

  python3 scripts/install_skills.py --dest ~/.codex/skills --all
  python3 scripts/install_skills.py --dest ~/.some-agent/skills debug-root-cause verify-change
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def available_skills(source: Path) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for item in sorted(source.iterdir() if source.is_dir() else []):
        if item.is_dir() and (item / "SKILL.md").is_file():
            skills[item.name] = item
    return skills


def install(source: Path, dest: Path, names: list[str], force: bool = False) -> list[Path]:
    choices = available_skills(source)
    missing = [name for name in names if name not in choices]
    if missing:
        raise ValueError(f"unknown skill(s): {', '.join(missing)}")

    dest.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []
    for name in names:
        target = dest / name
        if target.exists():
            if not force:
                raise FileExistsError(f"destination already exists: {target} (use --force to replace)")
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.copytree(choices[name], target)
        installed.append(target)
    return installed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install selected engineering-quality skills to an explicit directory.")
    parser.add_argument("skills", nargs="*", help="Skill names to copy")
    parser.add_argument("--dest", required=True, help="Destination skills directory")
    parser.add_argument("--all", action="store_true", help="Install all skills")
    parser.add_argument("--force", action="store_true", help="Replace existing destination skill folders")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    source = repo_root / "skills"
    choices = available_skills(source)
    names = sorted(choices) if args.all else args.skills
    if not names:
        parser.error("specify one or more skill names, or use --all")

    try:
        installed = install(source, Path(args.dest).expanduser().resolve(), names, args.force)
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    for path in installed:
        print(f"[OK] Installed {path.name} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
