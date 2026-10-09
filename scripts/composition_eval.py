#!/usr/bin/env python3
"""Validate, execute, and compare control/A/B/A+B skill-composition experiments."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.empirical_stats import bootstrap_mean_ci
    from scripts.live_eval import _run_arm
    from scripts.eval_provenance import sha256_file
    from scripts.live_eval_support import load_live_cases
except ModuleNotFoundError:
    from empirical_stats import bootstrap_mean_ci
    from live_eval import _run_arm
    from eval_provenance import sha256_file
    from live_eval_support import load_live_cases

ARMS = ("control", "a-only", "b-only", "combined")


def load_cases(path: Path, root: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("composition cases must be a non-empty list")
    live_by_id = {case["id"]: case for case in load_live_cases(root / "evals" / "live-cases.json", root)}
    seen = set()
    out = []
    for i, case in enumerate(data):
        if not isinstance(case, dict):
            raise ValueError(f"case {i} must be an object")
        cid = str(case.get("id", "")).strip()
        skills = case.get("skills")
        request = str(case.get("request", "")).strip()
        if not cid or cid in seen:
            raise ValueError(f"missing/duplicate case id: {cid!r}")
        seen.add(cid)
        if not isinstance(skills, list) or len(skills) != 2 or skills[0] == skills[1]:
            raise ValueError(f"{cid}: skills must contain exactly two distinct names")
        for skill in skills:
            if not (root / "skills" / skill / "SKILL.md").is_file():
                raise ValueError(f"{cid}: unknown skill {skill}")
        if not request:
            raise ValueError(f"{cid}: request is required")
        fixture = str(case.get("fixture", "")).strip()
        if not fixture or not (root / fixture).is_dir():
            raise ValueError(f"{cid}: missing fixture {fixture}")
        grader_case = str(case.get("grader_case", "")).strip()
        reference = live_by_id.get(grader_case)
        if not reference:
            raise ValueError(f"{cid}: grader_case must name a bundled live case")
        if str(reference.get("fixture")) != fixture:
            raise ValueError(f"{cid}: grader_case fixture must match composition fixture")
        resolved = dict(case)
        resolved["skill"] = "+".join(skills)
        resolved["evaluated_skills"] = list(skills)
        for key in ("setup", "pass_threshold", "graders", "manual_checks", "expected_change_globs"):
            if key not in resolved and key in reference:
                resolved[key] = reference[key]
        out.append(resolved)
    return out


def select_cases(cases: list[dict[str, Any]], requested: list[str]) -> list[dict[str, Any]]:
    if not requested:
        return cases
    wanted=set(requested)
    selected=[case for case in cases if str(case["id"]) in wanted]
    missing=sorted(wanted-{str(case["id"]) for case in selected})
    if missing:
        raise ValueError(f"unknown composition case(s): {', '.join(missing)}")
    return selected


def plan(cases: list[dict[str, Any]], provider: str, models: list[str], runs: int, campaign_id: str | None = None) -> list[dict[str, Any]]:
    rows = []
    for model in models or ["default"]:
        for case in cases:
            for n in range(1, runs + 1):
                for arm in ARMS:
                    enabled = [] if arm == "control" else [case["skills"][0]] if arm == "a-only" else [case["skills"][1]] if arm == "b-only" else list(case["skills"])
                    rows.append({
                        "campaign_id": campaign_id,
                        "case_id": case["id"], "provider": provider, "model": model, "run": n,
                        "arm": arm, "enabled_skills": enabled, "request": case["request"], "fixture": case.get("fixture"),
                    })
    return rows


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compare_records(path: Path, *, min_runs: int = 3, confidence: float = 0.95) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    groups: dict[tuple[str, str, str], dict[str, list[dict[str, Any]]]] = {}
    for row in rows:
        key = (str(row.get("provider", "unknown")), str(row.get("model") or "default"), str(row.get("case_id") or row.get("scenario_id") or "unknown"))
        groups.setdefault(key, {arm: [] for arm in ARMS})
        arm = str(row.get("arm") or row.get("mode") or "")
        if arm in ARMS and row.get("status", "completed") == "completed" and isinstance(row.get("score_fraction"), (int, float)):
            groups[key][arm].append(row)
    entries = []
    for (provider, model, case_id), arms in sorted(groups.items()):
        avg = {arm: _mean([float(r["score_fraction"]) for r in records]) for arm, records in arms.items()}
        counts = {arm: len(records) for arm, records in arms.items()}
        if any(counts[arm] < min_runs for arm in ARMS):
            classification = "INCONCLUSIVE"
            synergy_delta = None
            ci = [None, None]
        else:
            # Compare combined against the better single skill on matched run numbers.
            by_arm_run = {arm: {int(r.get("run", 0)): float(r["score_fraction"]) for r in records} for arm, records in arms.items()}
            common = sorted(set.intersection(*(set(v) for v in by_arm_run.values())))
            deltas = [by_arm_run["combined"][n] - max(by_arm_run["a-only"][n], by_arm_run["b-only"][n]) for n in common]
            synergy_delta = _mean(deltas)
            ci = list(bootstrap_mean_ci(deltas, confidence=confidence, samples=5000, seed=0)) if deltas else [None, None]
            if not deltas:
                classification = "INCONCLUSIVE"
            elif ci[1] is not None and ci[1] < -0.05:
                classification = "INTERFERENCE"
            elif ci[0] is not None and ci[0] > 0.05:
                classification = "SYNERGY"
            elif abs(synergy_delta or 0.0) <= 0.05:
                classification = "NEUTRAL_OR_REDUNDANT"
            else:
                classification = "INCONCLUSIVE"
        entries.append({
            "provider": provider, "model": model, "case_id": case_id, "classification": classification,
            "run_counts": counts, "mean_scores": avg, "combined_vs_best_single_delta": synergy_delta,
            "bootstrap_ci": ci, "confidence": confidence,
        })
    return {"schema_version": 2, "min_runs": min_runs, "confidence": confidence, "entries": entries}


def _campaign_id(provider: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"composition-{stamp}-{provider}-{uuid.uuid4().hex[:8]}"


def _completed_keys(path: Path, campaign_id: str) -> set[tuple[str, str, str, int, str]]:
    done: set[tuple[str, str, str, int, str]] = set()
    if not path.is_file():
        return done
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if item.get("campaign_id") != campaign_id or item.get("status") != "completed":
            continue
        done.add((str(item.get("provider")), str(item.get("model") or "default"), str(item.get("case_id") or item.get("scenario_id")), int(item.get("run", 0)), str(item.get("arm") or item.get("mode"))))
    return done


def run_cases(args: argparse.Namespace, cases: list[dict[str, Any]], root: Path, cases_path: Path) -> int:
    binary = args.binary or ("codex" if args.provider == "codex" else "claude" if args.provider == "claude" else "")
    if args.provider != "command" and not args.dry_run and shutil.which(binary) is None:
        print(f"[ERROR] provider binary not found: {binary}", file=sys.stderr)
        return 2
    if args.runs < 1:
        print("[ERROR] --runs must be at least 1", file=sys.stderr)
        return 2
    models = args.model or [None]
    out_root = args.output_dir.resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    records_path = out_root / f"{args.provider}-composition-runs.jsonl"
    if args.resume and not args.campaign_id:
        print("[ERROR] --resume requires --campaign-id", file=sys.stderr)
        return 2
    if records_path.exists() and not args.append and not args.resume:
        records_path.unlink()
    campaign_id = args.campaign_id or _campaign_id(args.provider)
    completed = _completed_keys(records_path, campaign_id) if args.resume else set()
    suite_hash = sha256_file(cases_path)
    count = 0
    for model in models:
        for case in cases:
            for repetition in range(1, args.runs + 1):
                order = ARMS if repetition % 2 else tuple(reversed(ARMS))
                for arm in order:
                    key=(args.provider, str(model or "default"), str(case["id"]), repetition, arm)
                    if key in completed:
                        print(f"[SKIP] {case['id']} model={model or 'default'} run={repetition} arm={arm} campaign={campaign_id}")
                        continue
                    enabled = [] if arm == "control" else [case["skills"][0]] if arm == "a-only" else [case["skills"][1]] if arm == "b-only" else list(case["skills"])
                    try:
                        record = _run_arm(
                            repo=root, case=case, provider=args.provider, binary=binary, model=model,
                            mode=arm, repetition=repetition, out_root=out_root, campaign_id=campaign_id,
                            suite_sha256=suite_hash, enabled_skill_names=enabled,
                            timeout_seconds=args.timeout_seconds, max_budget_usd=args.max_budget_usd,
                            command_json=args.command_json, dry_run=args.dry_run,
                        )
                    except (OSError, ValueError, RuntimeError) as exc:
                        print(f"[ERROR] {case['id']} {arm}: {exc}", file=sys.stderr)
                        return 1
                    record["arm"] = arm
                    record["case_id"] = case["id"]
                    with records_path.open("a", encoding="utf-8", newline="\n") as handle:
                        handle.write(json.dumps(record, sort_keys=True) + "\n")
                    count += 1
                    label = "PLAN" if args.dry_run else ("PASS" if record.get("passed") else "FAIL")
                    print(f"[{label}] {case['id']} model={model or 'default'} run={repetition} arm={arm}")
    print(f"[OK] Campaign {campaign_id}: wrote {count} composition record(s) to {records_path}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate, run, plan, or compare skill-composition interference evals.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--cases", type=Path, default=Path("evals/composition-cases.json"))
    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--cases", type=Path, default=Path("evals/composition-cases.json")); plan_p.add_argument("--case", action="append", default=[]); plan_p.add_argument("--provider", default="codex"); plan_p.add_argument("--model", action="append", default=[]); plan_p.add_argument("--runs", type=int, default=3); plan_p.add_argument("--campaign-id"); plan_p.add_argument("--output", type=Path)
    run_p = sub.add_parser("run")
    run_p.add_argument("--cases", type=Path, default=Path("evals/composition-cases.json")); run_p.add_argument("--case", action="append", default=[]); run_p.add_argument("--provider", choices=("codex", "claude", "command"), required=True); run_p.add_argument("--binary"); run_p.add_argument("--model", action="append", default=[]); run_p.add_argument("--runs", type=int, default=5); run_p.add_argument("--campaign-id"); run_p.add_argument("--timeout-seconds", type=int, default=900); run_p.add_argument("--max-budget-usd", type=float); run_p.add_argument("--output-dir", type=Path, default=Path(".verification/composition-evals")); run_p.add_argument("--command-json"); run_p.add_argument("--dry-run", action="store_true"); run_p.add_argument("--append", action="store_true"); run_p.add_argument("--resume", action="store_true")
    compare = sub.add_parser("compare")
    compare.add_argument("records", type=Path); compare.add_argument("--min-runs", type=int, default=3); compare.add_argument("--confidence", type=float, default=0.95); compare.add_argument("--fail-on-interference", action="store_true"); compare.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.cmd == "compare":
        try:
            result = compare_records(args.records, min_runs=args.min_runs, confidence=args.confidence)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr); return 2
        text = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return 1 if args.fail_on_interference and any(e["classification"] == "INTERFERENCE" for e in result["entries"]) else 0
    cases_path = args.cases if args.cases.is_absolute() else root / args.cases
    try:
        cases = load_cases(cases_path, root)
        if args.cmd in {"run", "plan"}:
            cases = select_cases(cases, args.case)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr); return 2
    if args.cmd == "validate":
        print(f"[OK] {len(cases)} composition case(s) validated"); return 0
    if args.cmd == "run":
        return run_cases(args, cases, root, cases_path)
    rows = plan(cases, args.provider, args.model, args.runs, args.campaign_id)
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    print(f"[OK] planned {len(rows)} composition arm(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
