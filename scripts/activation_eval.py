#!/usr/bin/env python3
"""Measure automatic Agent Skill activation against labeled prompts.

Real provider runs are opt-in. CI validates cases and dry-runs invocation wiring
without credentials or model spend. Detection is trace-based and may be UNKNOWN
when a host does not expose skill loading in its structured output.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.eval_provenance import repo_git_head, repo_version, runtime_metadata, sha256_file
    from scripts.live_eval_support import (
        build_antigravity_command,
        build_claude_command,
        build_codex_command,
        command_version,
        copy_skill_readonly,
        normalize_trace,
        prepare_claude_plugin_skills,
        run_process,
    )
except ModuleNotFoundError:
    from eval_provenance import repo_git_head, repo_version, runtime_metadata, sha256_file
    from live_eval_support import (
        build_antigravity_command,
        build_claude_command,
        build_codex_command,
        command_version,
        copy_skill_readonly,
        normalize_trace,
        prepare_claude_plugin_skills,
        run_process,
    )


def load_cases(path: Path, skill_names: set[str]) -> list[dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load activation cases: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError("activation cases must be a non-empty list")

    seen: set[str] = set()
    allowed = skill_names | {"none"}
    result: list[dict[str, str]] = []
    for index, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ValueError(f"activation case {index} must be an object")
        case_id = str(raw.get("id", "")).strip()
        prompt = str(raw.get("prompt", "")).strip()
        expected = str(raw.get("expected_primary_skill", "")).strip()
        if not case_id or case_id in seen:
            raise ValueError(f"activation case {index} has missing/duplicate id: {case_id!r}")
        seen.add(case_id)
        if not prompt:
            raise ValueError(f"activation case {case_id} has empty prompt")
        if expected not in allowed:
            raise ValueError(f"activation case {case_id} expects unknown skill: {expected}")
        result.append({"id": case_id, "prompt": prompt, "expected_primary_skill": expected})
    return result


def _all_skills(repo: Path) -> list[tuple[str, Path]]:
    skills: list[tuple[str, Path]] = []
    for path in sorted((repo / "skills").iterdir()):
        if path.is_dir() and (path / "SKILL.md").is_file():
            skills.append((path.name, path))
    return skills


def _custom_command(template_json: str, prompt: str, workspace: Path, run_dir: Path) -> list[str]:
    try:
        data = json.loads(template_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid --command-json: {exc}") from exc
    if not isinstance(data, list) or not data or not all(isinstance(x, str) and x for x in data):
        raise ValueError("--command-json must be a JSON array of non-empty strings")
    mapping = {"{prompt}": prompt, "{workspace}": str(workspace), "{run_dir}": str(run_dir)}
    result: list[str] = []
    for item in data:
        for key, value in mapping.items():
            item = item.replace(key, value)
        result.append(item)
    return result


def prepare_invocation(
    *,
    provider: str,
    binary: str,
    model: str | None,
    prompt: str,
    repo: Path,
    workspace: Path,
    run_dir: Path,
    command_json: str | None,
) -> tuple[list[str], dict[str, str] | None, str]:
    skills = _all_skills(repo)

    if provider in {"codex", "antigravity"}:
        for name, source in skills:
            copy_skill_readonly(source, workspace / ".agents" / "skills" / name)
        if provider == "codex":
            return build_codex_command(binary, prompt, model=model), None, "native-workspace-skills"
        return build_antigravity_command(binary, prompt, model=model), None, "native-workspace-skills"

    if provider == "claude":
        plugin_dir = prepare_claude_plugin_skills(run_dir, skills)
        return (
            build_claude_command(
                binary,
                prompt,
                plugin_dir=plugin_dir,
                control=False,
                model=model,
                max_budget_usd=None,
            ),
            None,
            "native-plugin-all-skills",
        )

    if provider == "command":
        if not command_json:
            raise ValueError("--command-json is required for provider=command")
        return _custom_command(command_json, prompt, workspace, run_dir), None, "custom-command"

    raise ValueError(f"unsupported provider: {provider}")


def detect_loaded_skills(raw_text: str, skill_names: list[str]) -> list[str]:
    """Return skill names in first-observed order from provider traces."""
    lowered = raw_text.lower().replace("\\", "/")
    found: list[tuple[int, str]] = []
    for name in skill_names:
        patterns = (
            f"/skills/{name}/skill.md",
            f".agents/skills/{name}/",
            f'"skill":"{name}"',
            f'"skill_name":"{name}"',
            f"/{name}",
        )
        positions = [lowered.find(pattern.lower()) for pattern in patterns]
        positions = [pos for pos in positions if pos >= 0]
        if positions:
            found.append((min(positions), name))
    return [name for _, name in sorted(found)]


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [r for r in records if r.get("status") == "completed"]
    detectable = [r for r in completed if r.get("detection_status") == "observed"]
    correct = [r for r in detectable if r.get("matched")]
    unknown = [r for r in completed if r.get("detection_status") == "unknown"]
    by_expected = Counter(str(r.get("expected_primary_skill")) for r in records)
    return {
        "records": len(records),
        "completed": len(completed),
        "detectable": len(detectable),
        "correct": len(correct),
        "accuracy_on_detectable": round(len(correct) / len(detectable), 4) if detectable else None,
        "unknown_detection": len(unknown),
        "expected_case_counts": dict(sorted(by_expected.items())),
    }


def run_command(args: argparse.Namespace, repo: Path) -> int:
    skill_names = {name for name, _ in _all_skills(repo)}
    cases_path = args.cases if args.cases.is_absolute() else repo / args.cases
    try:
        cases = load_cases(cases_path, skill_names)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    selected = cases
    if args.case:
        wanted = set(args.case)
        selected = [case for case in cases if case["id"] in wanted]
        missing = sorted(wanted - {case["id"] for case in selected})
        if missing:
            print(f"[ERROR] unknown activation case(s): {', '.join(missing)}", file=sys.stderr)
            return 2

    binary = args.binary or (
        "codex" if args.provider == "codex"
        else "claude" if args.provider == "claude"
        else "agy" if args.provider == "antigravity"
        else ""
    )
    if args.provider != "command" and not args.dry_run and shutil.which(binary) is None:
        print(f"[ERROR] provider binary not found: {binary}", file=sys.stderr)
        return 2

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / f"{args.provider}-activation.jsonl"
    if records_path.exists() and not args.append:
        records_path.unlink()

    records: list[dict[str, Any]] = []
    skill_list = sorted(skill_names)
    for case in selected:
        for repetition in range(1, args.runs + 1):
            run_dir = output_dir / args.provider / case["id"] / f"run-{repetition:03d}"
            if run_dir.exists():
                shutil.rmtree(run_dir)
            workspace = run_dir / "workspace"
            workspace.mkdir(parents=True)
            try:
                argv, extra_env, strategy = prepare_invocation(
                    provider=args.provider,
                    binary=binary,
                    model=args.model,
                    prompt=case["prompt"],
                    repo=repo,
                    workspace=workspace,
                    run_dir=run_dir,
                    command_json=args.command_json,
                )
            except (OSError, ValueError) as exc:
                print(f"[ERROR] {case['id']}: {exc}", file=sys.stderr)
                return 1

            base: dict[str, Any] = {
                "schema_version": 1,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "repo_version": repo_version(repo),
                "repo_commit": repo_git_head(repo),
                "suite_sha256": sha256_file(cases_path),
                "provider": args.provider,
                "provider_version": command_version(binary) if args.provider != "command" else "custom-command",
                "model": args.model,
                "case_id": case["id"],
                "run": repetition,
                "expected_primary_skill": case["expected_primary_skill"],
                "loading_strategy": strategy,
                **runtime_metadata(),
            }

            if args.dry_run:
                record = {**base, "status": "planned", "argv": argv}
            else:
                result = run_process(argv, cwd=workspace, timeout_seconds=args.timeout_seconds, env=extra_env)
                run_dir.mkdir(parents=True, exist_ok=True)
                (run_dir / "stdout.log").write_text(result.stdout, encoding="utf-8")
                (run_dir / "stderr.log").write_text(result.stderr, encoding="utf-8")
                trace, final = normalize_trace(result.stdout, result.stderr)
                observed = detect_loaded_skills(result.stdout + "\n" + result.stderr + "\n" + trace, skill_list)
                primary = observed[0] if observed else "none"
                expected = case["expected_primary_skill"]
                detection_status = "observed" if observed or expected == "none" else "unknown"
                matched = primary == expected if detection_status == "observed" else None
                record = {
                    **base,
                    "status": "timeout" if result.timed_out else ("completed" if result.exit_code == 0 else "provider-error"),
                    "exit_code": result.exit_code,
                    "duration_seconds": round(result.duration_seconds, 4),
                    "observed_skills": observed,
                    "observed_primary_skill": primary,
                    "detection_status": detection_status,
                    "matched": matched,
                    "final_response_excerpt": final[:500],
                }
            records.append(record)
            with records_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
            print(f"[{'PLAN' if args.dry_run else 'RUN'}] {case['id']} run={repetition} expected={case['expected_primary_skill']}")

    summary = summarize(records)
    (output_dir / f"{args.provider}-activation-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def validate_command(repo: Path, cases_path: Path) -> int:
    skill_names = {name for name, _ in _all_skills(repo)}
    try:
        cases = load_cases(cases_path, skill_names)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    counts = Counter(case["expected_primary_skill"] for case in cases)
    print(f"[OK] {len(cases)} activation cases validated")
    print("[INFO] positive cases: " + ", ".join(f"{name}={counts[name]}" for name in sorted(skill_names)))
    print(f"[INFO] none={counts['none']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate or run automatic skill-activation benchmarks.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--cases", type=Path, default=Path("evals/activation-cases.json"))

    run = sub.add_parser("run")
    run.add_argument("--cases", type=Path, default=Path("evals/activation-cases.json"))
    run.add_argument("--provider", choices=("codex", "claude", "antigravity", "command"), required=True)
    run.add_argument("--binary", default=None)
    run.add_argument("--model", default=None)
    run.add_argument("--runs", type=int, default=5)
    run.add_argument("--case", action="append", default=[])
    run.add_argument("--timeout-seconds", type=int, default=300)
    run.add_argument("--output-dir", type=Path, default=Path(".verification/activation-evals"))
    run.add_argument("--command-json", default=None)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--append", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    cases_path = args.cases if args.cases.is_absolute() else repo / args.cases
    if args.command == "validate":
        return validate_command(repo, cases_path)
    if args.runs < 1:
        print("[ERROR] --runs must be at least 1", file=sys.stderr)
        return 2
    return run_command(args, repo)


if __name__ == "__main__":
    sys.exit(main())
