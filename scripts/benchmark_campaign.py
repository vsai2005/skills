#!/usr/bin/env python3
"""Orchestrate repeatable, resumable empirical skill benchmark campaigns.

The script does not invent model evidence. It schedules real provider runs through
live_eval/composition_eval, records campaign provenance, and produces version-bound
statistical reports only from completed arms.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.eval_provenance import repo_git_head, repo_version, sha256_file
    from scripts.skill_effectiveness import build_registry, load_records, mark_freshness, render_markdown
    from scripts.composition_eval import compare_records
except ModuleNotFoundError:
    from eval_provenance import repo_git_head, repo_version, sha256_file
    from skill_effectiveness import build_registry, load_records, mark_freshness, render_markdown
    from composition_eval import compare_records


def load_policy(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("benchmark policy must be a schema_version=1 object")
    for key in ("default_repetitions", "minimum_pairs_for_claim", "bootstrap_samples"):
        if not isinstance(data.get(key), int) or int(data[key]) < 1:
            raise ValueError(f"invalid benchmark policy integer: {key}")
    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 < float(confidence) < 1:
        raise ValueError("benchmark policy confidence must be between 0 and 1")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("benchmark policy profiles must be a non-empty object")
    return data


def campaign_id(provider: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"empirical-{stamp}-{provider}-{uuid.uuid4().hex[:8]}"


def _run(argv: list[str], cwd: Path) -> int:
    result = subprocess.run(argv, cwd=cwd, check=False)
    return result.returncode


def _suite_counts(root: Path, profile: dict[str, Any], models: list[str], runs: int) -> dict[str, int]:
    import json as _json
    model_count = max(1, len(models))
    counts: dict[str, int] = {}
    if profile.get("local_live_cases"):
        cases = _json.loads((root / "evals" / "live-cases.json").read_text(encoding="utf-8"))
        counts["local_arms"] = len(cases) * runs * 2 * model_count
    if profile.get("historical_debug_cases"):
        cases = _json.loads((root / "evals" / "historical-debug-cases.json").read_text(encoding="utf-8"))
        counts["historical_arms"] = len(cases) * runs * 2 * model_count
    if profile.get("composition_cases"):
        cases = _json.loads((root / "evals" / "composition-cases.json").read_text(encoding="utf-8"))
        counts["composition_arms"] = len(cases) * runs * 4 * model_count
    counts["total_arms"] = sum(counts.values())
    return counts


def plan_campaign(root: Path, policy: dict[str, Any], *, provider: str, models: list[str], runs: int, profile_name: str, cid: str) -> dict[str, Any]:
    profile = policy["profiles"].get(profile_name)
    if not isinstance(profile, dict):
        raise ValueError(f"unknown benchmark profile: {profile_name}")
    return {
        "schema_version": 1,
        "campaign_id": cid,
        "provider": provider,
        "models": models or ["provider-default"],
        "runs_per_case": runs,
        "profile": profile_name,
        "suites": profile,
        "counts": _suite_counts(root, profile, models, runs),
        "policy_sha256": sha256_file(root / "evals" / "benchmark-policy.json"),
        "repo_version": repo_version(root),
        "repo_commit": repo_git_head(root),
    }


def analyze_campaign(root: Path, out_dir: Path, policy: dict[str, Any]) -> dict[str, Any]:
    record_paths = []
    for relative in ("local/codex-runs.jsonl", "local/claude-runs.jsonl", "historical/codex-runs.jsonl", "historical/claude-runs.jsonl"):
        path = out_dir / relative
        if path.is_file():
            record_paths.append(path)
    if not record_paths:
        raise ValueError("no completed live-eval record files found")
    registry = build_registry(
        load_records(record_paths),
        int(policy["minimum_pairs_for_claim"]),
        confidence=float(policy["confidence"]),
        bootstrap_samples=int(policy["bootstrap_samples"]),
        min_effect=float(policy["minimum_score_effect"]),
        costly_ratio=float(policy["costly_overhead_ratio"]),
    )
    mark_freshness(registry, root)
    (out_dir / "effectiveness-registry.json").write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "effectiveness-registry.md").write_text(render_markdown(registry), encoding="utf-8")
    strong = {
        **registry,
        "entries": [e for e in registry["entries"] if e.get("strong_evidence") and e.get("freshness") == "current"],
    }
    (out_dir / "effectiveness-registry-strong.json").write_text(json.dumps(strong, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    composition_outputs = []
    for provider in ("codex", "claude"):
        path = out_dir / "composition" / f"{provider}-composition-runs.jsonl"
        if path.is_file():
            result = compare_records(path, min_runs=max(3, int(policy["minimum_pairs_for_claim"])), confidence=float(policy["confidence"]))
            target = out_dir / "composition" / f"{provider}-composition-report.json"
            target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            composition_outputs.append(str(target))
    summary = {
        "schema_version": 1,
        "record_files": [str(path) for path in record_paths],
        "effectiveness_entries": len(registry["entries"]),
        "strong_current_entries": len(strong["entries"]),
        "harmful_strong_entries": sum(1 for e in strong["entries"] if e["classification"] == "HARMFUL"),
        "composition_reports": composition_outputs,
    }
    (out_dir / "analysis-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def run_campaign(args: argparse.Namespace, root: Path, policy: dict[str, Any]) -> int:
    if not args.dry_run and not args.model:
        print("[ERROR] real benchmark campaigns require at least one explicit --model; do not publish evidence for an unnamed provider default", file=sys.stderr)
        return 2
    if args.provider != "command" and not args.dry_run:
        binary = args.binary or ("codex" if args.provider == "codex" else "claude")
        if shutil.which(binary) is None:
            print(f"[ERROR] provider binary not found: {binary}", file=sys.stderr)
            return 2
    cid = args.campaign_id or campaign_id(args.provider)
    if args.resume and not args.campaign_id:
        print("[ERROR] --resume requires --campaign-id", file=sys.stderr)
        return 2
    runs = args.runs or int(policy["default_repetitions"])
    profile = policy["profiles"].get(args.profile)
    if not isinstance(profile, dict):
        print(f"[ERROR] unknown profile: {args.profile}", file=sys.stderr)
        return 2
    plan = plan_campaign(root, policy, provider=args.provider, models=args.model, runs=runs, profile_name=args.profile, cid=cid)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "campaign-plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return 0

    common = ["--provider", args.provider, "--runs", str(runs), "--campaign-id", cid, "--arm-order", str(policy.get("arm_order", "alternate"))]
    for model in args.model:
        common += ["--model", model]
    if args.binary:
        common += ["--binary", args.binary]
    if args.max_budget_usd is not None:
        common += ["--max-budget-usd", str(args.max_budget_usd)]
    if args.command_json:
        common += ["--command-json", args.command_json]
    if args.dry_run:
        common += ["--dry-run"]
    if args.resume:
        common += ["--resume"]
    manifest = {
        "schema_version": 1,
        "campaign_id": cid,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "plan": plan,
        "commands": [],
    }

    def execute(script: str, extra: list[str]) -> int:
        argv = [sys.executable, str(root / "scripts" / script), "run", *extra]
        manifest["commands"].append(argv)
        return _run(argv, root)

    if profile.get("local_live_cases"):
        rc = execute("live_eval.py", [*common, "--cases", "evals/live-cases.json", "--output-dir", str(out / "local")])
        if rc:
            return rc
    if profile.get("historical_debug_cases"):
        rc = execute("live_eval.py", [*common, "--cases", "evals/historical-debug-cases.json", "--output-dir", str(out / "historical")])
        if rc:
            return rc
    if profile.get("composition_cases"):
        comp_common = ["--provider", args.provider, "--runs", str(runs), "--campaign-id", cid]
        for model in args.model:
            comp_common += ["--model", model]
        if args.binary:
            comp_common += ["--binary", args.binary]
        if args.max_budget_usd is not None:
            comp_common += ["--max-budget-usd", str(args.max_budget_usd)]
        if args.command_json:
            comp_common += ["--command-json", args.command_json]
        if args.dry_run:
            comp_common += ["--dry-run"]
        if args.resume:
            comp_common += ["--resume"]
        rc = execute("composition_eval.py", [*comp_common, "--output-dir", str(out / "composition")])
        if rc:
            return rc

    manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "campaign-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not args.dry_run:
        try:
            summary = analyze_campaign(root, out, policy)
        except ValueError as exc:
            print(f"[ERROR] analysis failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(summary, indent=2))
    print(f"[OK] Campaign {cid} complete at {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or analyze empirical coding-skill benchmark campaigns.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--policy", type=Path, default=Path("evals/benchmark-policy.json"))
    plan = sub.add_parser("plan")
    run = sub.add_parser("run")
    analyze = sub.add_parser("analyze")
    for cmd in (plan, run):
        cmd.add_argument("--policy", type=Path, default=Path("evals/benchmark-policy.json"))
        cmd.add_argument("--provider", choices=("codex", "claude", "command"), required=True)
        cmd.add_argument("--model", action="append", default=[])
        cmd.add_argument("--runs", type=int)
        cmd.add_argument("--profile", choices=("core", "full"), default="core")
        cmd.add_argument("--campaign-id")
        cmd.add_argument("--output-dir", type=Path, default=Path(".verification/empirical-benchmark"))
    run.add_argument("--binary")
    run.add_argument("--max-budget-usd", type=float)
    run.add_argument("--command-json")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--plan-only", action="store_true")
    analyze.add_argument("--policy", type=Path, default=Path("evals/benchmark-policy.json"))
    analyze.add_argument("--output-dir", type=Path, default=Path(".verification/empirical-benchmark"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    policy_path = args.policy if args.policy.is_absolute() else root / args.policy
    try:
        policy = load_policy(policy_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    if args.cmd == "validate":
        print(f"[OK] benchmark policy validated: {policy_path}")
        return 0
    if args.cmd == "analyze":
        try:
            summary = analyze_campaign(root, args.output_dir.resolve(), policy)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 2
        print(json.dumps(summary, indent=2))
        return 0
    runs = args.runs or int(policy["default_repetitions"])
    cid = args.campaign_id or campaign_id(args.provider)
    if args.cmd == "plan":
        try:
            result = plan_campaign(root, policy, provider=args.provider, models=args.model, runs=runs, profile_name=args.profile, cid=cid)
        except ValueError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return run_campaign(args, root, policy)


if __name__ == "__main__":
    raise SystemExit(main())
