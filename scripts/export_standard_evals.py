#!/usr/bin/env python3
"""Export central behavior cases to Agent Skills evals/evals.json-compatible files."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def load_behavior_cases(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load behavior cases: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("behavior cases must be a list")
    return data


def export_cases(root: Path, output_dir: Path) -> list[Path]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    cases = load_behavior_cases(root / "evals" / "behavior-cases.json")
    skill_names = sorted(
        path.name for path in (root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    written: list[Path] = []
    for skill in skill_names:
        selected = [
            case for case in cases
            if case.get("skills") == [skill]
        ]
        if not selected:
            raise ValueError(f"no single-skill behavior case available for {skill}")
        evals = []
        for index, case in enumerate(selected, start=1):
            expected = [str(item) for item in case.get("expected_behaviors", [])]
            evals.append(
                {
                    "id": index,
                    "prompt": str(case["request"]),
                    "expected_output": " ".join(expected),
                    "files": [],
                    "assertions": expected,
                    "source_case_id": str(case["id"]),
                }
            )
        target = output_dir / skill / "evals" / "evals.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"skill_name": skill, "evals": evals}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export standard Agent Skills eval files.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("dist/standard-evals"))
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    try:
        written = export_cases(root, output)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] Exported {len(written)} standard eval file(s) to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
