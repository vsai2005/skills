#!/usr/bin/env python3
"""Validate and measure a non-enforced skill invocation classification.

This experiment estimates how much discovery metadata could be removed from
model-visible routing if selected workflow skills became explicitly invoked.
It does not change any host metadata or activation behavior.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.context_budget import measure
except ModuleNotFoundError:  # direct script execution from scripts/
    from context_budget import measure

CLASSES = ("model-default", "explicit-candidate", "undecided")


def load_policy(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load invocation policy {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("invocation policy must be a schema_version=1 object")
    classes = data.get("classes")
    if not isinstance(classes, dict):
        raise ValueError("invocation policy classes must be an object")
    unknown = sorted(set(classes) - set(CLASSES))
    missing = sorted(set(CLASSES) - set(classes))
    if unknown or missing:
        detail = []
        if unknown:
            detail.append("unknown: " + ", ".join(unknown))
        if missing:
            detail.append("missing: " + ", ".join(missing))
        raise ValueError("invalid invocation classes (" + "; ".join(detail) + ")")
    for name in CLASSES:
        values = classes[name]
        if not isinstance(values, list) or not all(isinstance(x, str) and x for x in values):
            raise ValueError(f"invocation class {name!r} must be a list of skill names")
    if data.get("enforced") is not False:
        raise ValueError("Phase 4E invocation policy must remain non-enforced")
    return data


def validate_policy(root: Path, policy: dict[str, Any]) -> list[str]:
    skills = {item.name for item in measure(root)}
    classes = policy["classes"]
    listed = [skill for class_name in CLASSES for skill in classes[class_name]]

    problems: list[str] = []
    duplicates = sorted({skill for skill in listed if listed.count(skill) > 1})
    if duplicates:
        problems.append("skill(s) classified more than once: " + ", ".join(duplicates))

    listed_set = set(listed)
    missing = sorted(skills - listed_set)
    unknown = sorted(listed_set - skills)
    if missing:
        problems.append("unclassified skill(s): " + ", ".join(missing))
    if unknown:
        problems.append("unknown classified skill(s): " + ", ".join(unknown))
    return problems


def report(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    budgets = {item.name: item for item in measure(root)}
    problems = validate_policy(root, policy)
    if problems:
        raise ValueError("; ".join(problems))

    explicit = list(policy["classes"]["explicit-candidate"])
    undecided = list(policy["classes"]["undecided"])
    model_default = list(policy["classes"]["model-default"])

    total_chars = sum(item.discovery_chars for item in budgets.values())
    candidate_chars = sum(budgets[name].discovery_chars for name in explicit)
    hypothetical_chars = total_chars - candidate_chars

    return {
        "schema_version": 1,
        "enforced": False,
        "skills": len(budgets),
        "classification_counts": {
            "model-default": len(model_default),
            "explicit-candidate": len(explicit),
            "undecided": len(undecided),
        },
        "discovery": {
            "current_chars": total_chars,
            "current_rough_tokens": math.ceil(total_chars / 4),
            "explicit_candidate_chars": candidate_chars,
            "explicit_candidate_rough_tokens": math.ceil(candidate_chars / 4),
            "hypothetical_model_visible_chars": hypothetical_chars,
            "hypothetical_model_visible_rough_tokens": math.ceil(hypothetical_chars / 4),
            "hypothetical_reduction_fraction": (
                round(candidate_chars / total_chars, 6) if total_chars else 0.0
            ),
        },
        "classes": {
            "explicit-candidate": explicit,
            "undecided": undecided,
            "model-default": model_default,
        },
        "claim_boundary": (
            "Hypothetical discovery-only estimate. No host invocation policy changes "
            "are applied, and no activation-quality claim is made."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or report the non-enforced invocation classification experiment."
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("evals/invocation-policy.json"),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    policy_path = args.policy if args.policy.is_absolute() else root / args.policy
    try:
        policy = load_policy(policy_path)
        result = report(root, policy)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        counts = result["classification_counts"]
        discovery = result["discovery"]
        print(
            f"Invocation classification: {result['skills']} skills; "
            f"{counts['model-default']} model-default, "
            f"{counts['explicit-candidate']} explicit-candidate, "
            f"{counts['undecided']} undecided"
        )
        print(
            "Discovery experiment: "
            f"{discovery['current_chars']} -> "
            f"{discovery['hypothetical_model_visible_chars']} chars "
            f"if explicit candidates were withheld "
            f"({discovery['hypothetical_reduction_fraction']:.1%} hypothetical reduction)"
        )
        print("Policy enforcement: OFF")
        print(result["claim_boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
