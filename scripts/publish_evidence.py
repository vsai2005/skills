#!/usr/bin/env python3
"""Publish sanitized, current real-model effectiveness claims.

Input is the strong registry produced by benchmark_campaign.py / skill_effectiveness.py.
Only strong, current, exact-skill-hash entries with an explicit provider and model
are publishable. Raw traces, prompts, responses, fixtures, and private data are
never copied into the public evidence registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.eval_provenance import sha256_tree
    from scripts.evidence_freshness import load_registry, validate_claims
except ModuleNotFoundError:
    from eval_provenance import sha256_tree
    from evidence_freshness import load_registry, validate_claims


def _load_input(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load effectiveness registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("effectiveness registry must use schema_version=2")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("effectiveness registry entries must be a list")
    return data


def _tested_at(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("--tested-at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("--tested-at must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower()
    return value[:80] or "unknown"


def sanitize_claims(root: Path, source: dict[str, Any], tested_at: str) -> list[dict[str, Any]]:
    published: list[dict[str, Any]] = []
    for entry in source["entries"]:
        if not isinstance(entry, dict):
            continue
        if not entry.get("strong_evidence") or entry.get("freshness") != "current":
            continue

        host = str(entry.get("provider") or "").strip()
        model = str(entry.get("model") or "").strip()
        skill = str(entry.get("skill") or "").strip()
        skill_sha = str(entry.get("skill_sha256") or "").strip()
        classification = str(entry.get("classification") or "").strip()
        pairs = entry.get("pairs")

        if not host or host in {"unknown", "default"}:
            raise ValueError(f"strong entry for {skill or '(unknown)'} has no concrete provider")
        if not model or model in {"default", "provider-default", "unknown"}:
            raise ValueError(f"strong entry for {skill or '(unknown)'} has no explicit model")
        skill_dir = root / "skills" / skill
        if not (skill_dir / "SKILL.md").is_file():
            raise ValueError(f"strong entry names missing skill: {skill}")
        current_sha = sha256_tree(skill_dir)
        if skill_sha != current_sha:
            raise ValueError(f"strong entry for {skill} is stale: {skill_sha} != {current_sha}")
        if classification not in {"BENEFICIAL", "HARMFUL"}:
            raise ValueError(
                f"strong entry for {skill} has non-publishable classification: {classification}"
            )
        if not isinstance(pairs, int) or pairs < 1:
            raise ValueError(f"strong entry for {skill} has invalid pairs count")

        claim_id = f"{_slug(host)}-{_slug(model)}-{_slug(skill)}-{skill_sha[:12]}"
        claim = {
            "id": claim_id,
            "skill": skill,
            "host": host,
            "model": model,
            "status": classification,
            "tested_at": tested_at,
            "skill_sha256": skill_sha,
            "paired_runs": pairs,
            "score_delta": entry.get("score_delta"),
            "bootstrap_ci": entry.get("bootstrap_ci"),
            "confidence": entry.get("confidence"),
            "token_ratio": entry.get("token_ratio"),
            "time_ratio": entry.get("time_ratio"),
            "campaigns": list(entry.get("campaigns") or []),
        }
        published.append(claim)
    return published


def publish(
    root: Path,
    source_path: Path,
    output_path: Path,
    tested_at: str,
    *,
    replace: bool,
) -> dict[str, Any]:
    source = _load_input(source_path)
    new_claims = sanitize_claims(root, source, _tested_at(tested_at))
    if not new_claims:
        raise ValueError("no strong current entries are eligible for publication")

    if output_path.exists():
        registry = load_registry(output_path)
    else:
        registry = {"schema_version": 1, "max_age_days": 90, "claims": []}

    existing = [] if replace else list(registry.get("claims") or [])
    by_id = {str(item.get("id")): item for item in existing if isinstance(item, dict)}
    for claim in new_claims:
        by_id[claim["id"]] = claim
    registry["claims"] = sorted(by_id.values(), key=lambda item: str(item.get("id")))

    problems = validate_claims(root, registry)
    if problems:
        raise ValueError("published registry would be invalid: " + "; ".join(problems))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish sanitized strong/current benchmark claims to evidence/registry.json."
    )
    parser.add_argument("source", type=Path, help="effectiveness-registry-strong.json")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("evidence/registry.json"))
    parser.add_argument("--tested-at", required=True, help="ISO-8601 timestamp for the real campaign")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    source = args.source if args.source.is_absolute() else root / args.source
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        registry = publish(
            root,
            source,
            output,
            args.tested_at,
            replace=args.replace,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] Published {len(registry['claims'])} current empirical claim(s) -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
