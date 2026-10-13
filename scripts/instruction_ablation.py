#!/usr/bin/env python3
"""Create section-ablated skill variants and compare token-aware experiment records.

This tool identifies *candidates* for human review. It never removes instructions
from the source skill. Protected safety/contract instructions are never emitted
as prune candidates.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any

HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.M)


def remove_section(text: str, title: str) -> str:
    matches = list(HEADING.finditer(text))
    target = None
    norm = lambda value: re.sub(r"^\d+\.\s*", "", value.strip()).casefold()
    for index, match in enumerate(matches):
        if norm(match.group(2)) == norm(title):
            target = (index, match)
            break
    if target is None:
        raise ValueError(f"section not found: {title}")

    index, match = target
    level = len(match.group(1))
    end = len(text)
    for nxt in matches[index + 1 :]:
        if len(nxt.group(1)) <= level:
            end = nxt.start()
            break
    return text[: match.start()] + text[end:]


def create_variant(skill_dir: Path, title: str, out: Path) -> Path:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(skill_dir, out)
    skill_md = out / "SKILL.md"
    skill_md.write_text(
        remove_section(skill_md.read_text(encoding="utf-8"), title),
        encoding="utf-8",
    )
    return skill_md


def _avg(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 6) if values else None


def _metric(record: dict[str, Any], name: str) -> float | None:
    if name == "score":
        value = record.get("score_fraction")
    elif name == "duration_seconds":
        value = record.get("duration_seconds")
    elif name == "tool_events":
        value = (record.get("workflow_metrics") or {}).get("tool_event_count")
    elif name == "input_tokens":
        value = (record.get("usage") or {}).get("input_tokens")
    elif name == "output_tokens":
        value = (record.get("usage") or {}).get("output_tokens")
    elif name == "cached_input_tokens":
        usage = record.get("usage") or {}
        value = usage.get("cached_input_tokens")
        if value is None:
            value = usage.get("cache_read_input_tokens")
    elif name == "tokens":
        usage = record.get("usage") or {}
        value = usage.get("total_tokens")
        if value is None:
            value = usage.get("tokens")
        if value is None:
            inp = usage.get("input_tokens")
            out = usage.get("output_tokens")
            if isinstance(inp, (int, float)) and isinstance(out, (int, float)):
                value = inp + out
    else:
        raise ValueError(f"unknown metric: {name}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _variant_metrics(rows: list[dict[str, Any]], variant: str) -> dict[str, float | int | None]:
    selected = [
        row
        for row in rows
        if row.get("variant") == variant and row.get("status", "completed") == "completed"
    ]

    result: dict[str, float | int | None] = {"records": len(selected)}
    for metric in (
        "score",
        "tokens",
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "duration_seconds",
        "tool_events",
    ):
        values = [
            value
            for row in selected
            if (value := _metric(row, metric)) is not None
        ]
        result[metric] = _avg(values)

    pass_values = [
        1.0 if bool(row.get("passed")) else 0.0
        for row in selected
        if "passed" in row
    ]
    result["pass_rate"] = _avg(pass_values)
    return result


def _ratio(after: float | int | None, before: float | int | None) -> float | None:
    if not isinstance(after, (int, float)) or not isinstance(before, (int, float)):
        return None
    if before <= 0:
        return None
    return round(float(after) / float(before), 6)


def _delta(after: float | int | None, before: float | int | None) -> float | None:
    if not isinstance(after, (int, float)) or not isinstance(before, (int, float)):
        return None
    return round(float(after) - float(before), 6)


def compare(
    path: Path,
    *,
    score_tolerance: float = 0.01,
    min_token_reduction: float = 0.02,
    max_cost_regression: float = 0.10,
    protected: bool = False,
) -> dict[str, Any]:
    rows = [
        json.loads(raw)
        for raw in path.read_text(encoding="utf-8").splitlines()
        if raw.strip()
    ]

    metrics = {
        variant: _variant_metrics(rows, variant)
        for variant in ("control", "full", "ablated")
    }
    averages = {
        variant: metrics[variant]["score"]
        for variant in ("control", "full", "ablated")
    }

    full = metrics["full"]
    ablated = metrics["ablated"]
    full_score = full["score"]
    ablated_score = ablated["score"]
    full_tokens = full["tokens"]
    ablated_tokens = ablated["tokens"]

    protected_from_records = any(
        row.get("protected_instruction") is True
        for row in rows
        if row.get("variant") in {"full", "ablated"}
    )
    is_protected = protected or protected_from_records

    score_delta = _delta(ablated_score, full_score)
    token_ratio = _ratio(ablated_tokens, full_tokens)
    time_ratio = _ratio(ablated["duration_seconds"], full["duration_seconds"])
    tool_ratio = _ratio(ablated["tool_events"], full["tool_events"])
    token_savings = None if token_ratio is None else round(1.0 - token_ratio, 6)

    checks: dict[str, bool | None] = {
        "protected": is_protected,
        "quality_non_inferior": (
            None
            if score_delta is None
            else score_delta >= -score_tolerance
        ),
        "token_data_available": token_ratio is not None,
        "token_savings_meets_threshold": (
            None
            if token_savings is None
            else token_savings >= min_token_reduction
        ),
        "time_regressed_materially": (
            None
            if time_ratio is None
            else time_ratio > 1.0 + max_cost_regression
        ),
        "tool_events_regressed_materially": (
            None
            if tool_ratio is None
            else tool_ratio > 1.0 + max_cost_regression
        ),
    }

    if full_score is None or ablated_score is None:
        decision = "INSUFFICIENT_DATA"
    elif is_protected:
        decision = "PROTECTED_KEEP"
    elif not checks["quality_non_inferior"]:
        decision = "KEEP_SECTION"
    elif token_ratio is None:
        decision = "INSUFFICIENT_TOKEN_DATA"
    elif not checks["token_savings_meets_threshold"]:
        decision = "NO_MATERIAL_TOKEN_SAVINGS"
    elif checks["time_regressed_materially"] or checks["tool_events_regressed_materially"]:
        decision = "COST_REGRESSION_KEEP"
    else:
        decision = "PRUNE_CANDIDATE"

    return {
        "averages": averages,
        "metrics": metrics,
        "deltas": {
            "score": score_delta,
            "tokens": _delta(ablated_tokens, full_tokens),
            "token_ratio": token_ratio,
            "token_savings_fraction": token_savings,
            "duration_ratio": time_ratio,
            "tool_event_ratio": tool_ratio,
        },
        "checks": checks,
        "policy": {
            "score_tolerance": score_tolerance,
            "minimum_token_reduction": min_token_reduction,
            "maximum_cost_regression": max_cost_regression,
            "protected_rules_never_prune": True,
            "prune_candidate_requires": (
                "quality non-inferior + token data + minimum token savings + "
                "no material time/tool-event regression + not protected"
            ),
        },
        "decision": decision,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create or compare token-aware instruction ablation experiments."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create")
    create.add_argument("skill_dir", type=Path)
    create.add_argument("--section", required=True)
    create.add_argument("--output-dir", type=Path, required=True)

    compare_cmd = sub.add_parser("compare")
    compare_cmd.add_argument("records", type=Path)
    compare_cmd.add_argument("--score-tolerance", type=float, default=0.01)
    compare_cmd.add_argument("--min-token-reduction", type=float, default=0.02)
    compare_cmd.add_argument("--max-cost-regression", type=float, default=0.10)
    compare_cmd.add_argument(
        "--protected",
        action="store_true",
        help="Mark the tested instruction as a mandatory safety/contract rule.",
    )
    compare_cmd.add_argument("--fail-on-prune-candidate", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "create":
            print(
                create_variant(
                    args.skill_dir.resolve(),
                    args.section,
                    args.output_dir.resolve(),
                )
            )
            return 0

        if args.score_tolerance < 0:
            raise ValueError("--score-tolerance must be >= 0")
        if not 0 <= args.min_token_reduction < 1:
            raise ValueError("--min-token-reduction must be in [0, 1)")
        if args.max_cost_regression < 0:
            raise ValueError("--max-cost-regression must be >= 0")

        result = compare(
            args.records,
            score_tolerance=args.score_tolerance,
            min_token_reduction=args.min_token_reduction,
            max_cost_regression=args.max_cost_regression,
            protected=args.protected,
        )
        print(json.dumps(result, indent=2))
        return (
            1
            if args.fail_on_prune_candidate
            and result["decision"] == "PRUNE_CANDIDATE"
            else 0
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
