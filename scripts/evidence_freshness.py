#!/usr/bin/env python3
"""Validate freshness of published real-model skill-effectiveness claims."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.eval_provenance import sha256_tree
except ModuleNotFoundError:
    from eval_provenance import sha256_tree


ALLOWED_STATUSES = {
    "BENEFICIAL",
    "NEUTRAL",
    "COSTLY",
    "HARMFUL",
    "PROMISING",
    "POSSIBLY_HARMFUL",
    "INSUFFICIENT_DATA",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_registry(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load evidence registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("evidence registry must be an object with schema_version=1")
    max_age = data.get("max_age_days")
    if not isinstance(max_age, int) or max_age < 1:
        raise ValueError("max_age_days must be a positive integer")
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    return data


def validate_claims(root: Path, registry: dict[str, Any], now: datetime | None = None) -> list[str]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    max_age_days = int(registry["max_age_days"])
    problems: list[str] = []
    seen: set[str] = set()

    for index, claim in enumerate(registry["claims"]):
        if not isinstance(claim, dict):
            problems.append(f"claim {index} must be an object")
            continue
        claim_id = str(claim.get("id", "")).strip()
        skill = str(claim.get("skill", "")).strip()
        host = str(claim.get("host", "")).strip()
        model = str(claim.get("model", "")).strip()
        status = str(claim.get("status", "")).strip()
        tested_at = str(claim.get("tested_at", "")).strip()
        skill_sha = str(claim.get("skill_sha256", "")).strip()
        pairs = claim.get("paired_runs")

        if not claim_id or claim_id in seen:
            problems.append(f"claim {index} has missing/duplicate id: {claim_id!r}")
        seen.add(claim_id)
        if not skill or not host or not model:
            problems.append(f"claim {claim_id or index} must name skill, host, and model")
        if status not in ALLOWED_STATUSES:
            problems.append(f"claim {claim_id or index} has invalid status: {status!r}")
        if not isinstance(pairs, int) or pairs < 1:
            problems.append(f"claim {claim_id or index} paired_runs must be >= 1")

        skill_dir = root / "skills" / skill
        if skill and not (skill_dir / "SKILL.md").is_file():
            problems.append(f"claim {claim_id or index} names missing skill: {skill}")
        elif skill:
            current_sha = sha256_tree(skill_dir)
            if skill_sha != current_sha:
                problems.append(
                    f"claim {claim_id or index} is stale: skill hash {skill_sha or '(missing)'} != {current_sha}"
                )

        try:
            tested = _parse_utc(tested_at)
        except (ValueError, TypeError):
            problems.append(f"claim {claim_id or index} has invalid tested_at: {tested_at!r}")
            continue
        age_days = (now - tested).total_seconds() / 86400.0
        if age_days < -1:
            problems.append(f"claim {claim_id or index} tested_at is in the future")
        elif age_days > max_age_days:
            problems.append(
                f"claim {claim_id or index} is stale: {age_days:.1f} days old > {max_age_days}"
            )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check freshness of published empirical skill claims.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("evidence/registry.json"))
    args = parser.parse_args(argv)

    root = args.root.resolve()
    registry_path = args.registry if args.registry.is_absolute() else root / args.registry
    try:
        registry = load_registry(registry_path)
        problems = validate_claims(root, registry)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}", file=sys.stderr)
        return 1

    claims = registry["claims"]
    if not claims:
        print("[OK] Evidence registry is valid; no real-model effectiveness claims are currently published")
    else:
        print(f"[OK] {len(claims)} published claim(s) are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
