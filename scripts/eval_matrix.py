#!/usr/bin/env python3
"""Create a provider-neutral RED/GREEN run matrix for behavior eval scenarios.

The output is a plan, not a model evaluator. Feed each JSONL record to the
actual coding-agent harness you want to benchmark, preserving the same fixture
and request for control (skill disabled) and treatment (skill enabled) runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_cases(path: Path) -> list[dict[str, object]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load behavior evals: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("behavior evals must be a JSON list")
    result: list[dict[str, object]] = []
    for index, case in enumerate(data):
        if not isinstance(case, dict) or not case.get("id") or not case.get("request"):
            raise ValueError(f"invalid behavior case at index {index}")
        skills = case.get("skills")
        if not isinstance(skills, list) or not skills:
            raise ValueError(f"behavior case {case.get('id')} has no skills")
        result.append(case)
    return result


def build_matrix(cases: list[dict[str, object]], runs: int) -> list[dict[str, object]]:
    if runs < 1:
        raise ValueError("runs must be at least 1")
    matrix: list[dict[str, object]] = []
    for case in cases:
        primary_skill = str(case["skills"][0])
        for run in range(1, runs + 1):
            for mode in ("control", "treatment"):
                matrix.append(
                    {
                        "scenario_id": str(case["id"]),
                        "run": run,
                        "mode": mode,
                        "skill": primary_skill if mode == "treatment" else None,
                        "fixture": str(case.get("fixture", "")),
                        "request": str(case["request"]),
                        "expected_behaviors": list(case.get("expected_behaviors", [])),
                    }
                )
    return matrix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit RED/GREEN behavior-eval run plans as JSONL.")
    parser.add_argument("--cases", type=Path, default=Path("evals/behavior-cases.json"))
    parser.add_argument("--runs", type=int, default=3, help="Repetitions per control/treatment arm (default: 3)")
    parser.add_argument("--output", type=Path, default=None, help="Write JSONL here instead of stdout")
    args = parser.parse_args(argv)
    try:
        matrix = build_matrix(load_cases(args.cases), args.runs)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    text = "".join(json.dumps(item, sort_keys=True) + "\n" for item in matrix)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"[OK] Wrote {len(matrix)} planned runs to {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
