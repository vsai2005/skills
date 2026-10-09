#!/usr/bin/env python3
"""Run live RED/GREEN skill evaluations through Codex, Claude Code, or a custom command.

Every arm gets a fresh disposable copy of the same fixture. Raw provider output,
normalized trace text, repository changes, deterministic grader results, and
best-effort usage data are retained for auditability.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import uuid
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.eval_provenance import repo_git_head, repo_version, runtime_metadata, sha256_file, sha256_json, sha256_tree
    from scripts.live_eval_graders import grade_case
    from scripts.live_eval_support import (
        build_claude_command,
        build_codex_command,
        command_version,
        copy_skill_readonly,
        expand_argv,
        extract_usage,
        git_changed_files,
        git_diff_metrics,
        trace_workflow_metrics,
        load_live_cases,
        normalize_trace,
        prepare_claude_plugin,
        prepare_claude_plugin_skills,
        prepare_prompt_skill,
        prepare_prompt_skills,
        run_process,
    )
except ModuleNotFoundError:
    from eval_provenance import repo_git_head, repo_version, runtime_metadata, sha256_file, sha256_json, sha256_tree
    from live_eval_graders import grade_case
    from live_eval_support import (
        build_claude_command,
        build_codex_command,
        command_version,
        copy_skill_readonly,
        expand_argv,
        extract_usage,
        git_changed_files,
        git_diff_metrics,
        trace_workflow_metrics,
        load_live_cases,
        normalize_trace,
        prepare_claude_plugin,
        prepare_claude_plugin_skills,
        prepare_prompt_skill,
        prepare_prompt_skills,
        run_process,
    )


def _run_checked(argv: list[str], cwd: Path, timeout: int = 60) -> None:
    result = run_process(argv, cwd=cwd, timeout_seconds=timeout)
    if result.timed_out or result.exit_code != 0:
        raise RuntimeError(
            f"setup command failed: {argv!r}; exit={result.exit_code}; "
            f"stdout={result.stdout[-500:]!r}; stderr={result.stderr[-500:]!r}"
        )


def _ensure_git(workspace: Path) -> None:
    if (workspace / ".git").exists():
        return
    _run_checked(["git", "init", "-q"], workspace)
    _run_checked(["git", "config", "user.email", "live-eval@example.invalid"], workspace)
    _run_checked(["git", "config", "user.name", "Live Eval"], workspace)
    _run_checked(["git", "add", "-A"], workspace)
    _run_checked(["git", "commit", "-q", "-m", "fixture baseline"], workspace)


def _copy_fixture(repo: Path, case: dict[str, Any], workspace: Path, run_dir: Path) -> None:
    git_fixture = case.get("git_fixture")
    if git_fixture:
        workspace.mkdir(parents=True)
        repo_url = str(git_fixture["repo_url"])
        base_commit = str(git_fixture["base_commit"])
        _run_checked(["git", "init", "-q"], workspace)
        _run_checked(["git", "remote", "add", "origin", repo_url], workspace)
        _run_checked(["git", "fetch", "--depth=1", "origin", base_commit], workspace, timeout=int(case.get("setup_timeout_seconds", 120)))
        _run_checked(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], workspace)
    else:
        fixture = (repo / str(case["fixture"])).resolve()
        shutil.copytree(fixture, workspace)
    for command in case.get("setup", []):
        argv = expand_argv(list(command), workspace=workspace, repo=repo, run_dir=run_dir)
        _run_checked(argv, workspace, timeout=int(case.get("setup_timeout_seconds", 60)))
    _ensure_git(workspace)


def _custom_command(template_json: str, prompt: str, workspace: Path, run_dir: Path) -> list[str]:
    try:
        data = json.loads(template_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid --command-json: {exc}") from exc
    if not isinstance(data, list) or not data or not all(isinstance(x, str) and x for x in data):
        raise ValueError("--command-json must be a JSON array of non-empty strings")
    mapping = {
        "{prompt}": prompt,
        "{workspace}": str(workspace),
        "{run_dir}": str(run_dir),
    }
    result: list[str] = []
    for item in data:
        for key, value in mapping.items():
            item = item.replace(key, value)
        result.append(item)
    return result


def _provider_invocation(
    *,
    provider: str,
    binary: str,
    model: str | None,
    prompt: str,
    enabled_skills: list[tuple[str, Path]],
    workspace: Path,
    run_dir: Path,
    max_budget_usd: float | None,
    command_json: str | None,
) -> tuple[list[str], dict[str, str] | None, str, str]:
    """Return argv, extra env, loading strategy, and final prompt."""
    control = not enabled_skills
    if provider == "claude":
        plugin_dir = None if control else prepare_claude_plugin_skills(run_dir, enabled_skills)
        argv = build_claude_command(
            binary, prompt, plugin_dir=plugin_dir, control=control, model=model, max_budget_usd=max_budget_usd
        )
        return argv, None, "disabled-skills" if control else "native-plugin", prompt

    final_prompt = prompt
    strategy = "no-skill"
    if enabled_skills:
        _, instruction = prepare_prompt_skills(workspace, enabled_skills)
        final_prompt = f"{instruction}\n\nTask:\n{prompt}"
        strategy = "prompt-mounted-skills"
    if provider == "codex":
        return build_codex_command(binary, final_prompt, model=model), None, strategy, final_prompt
    if provider == "command":
        if not command_json:
            raise ValueError("--command-json is required for provider=command")
        return _custom_command(command_json, final_prompt, workspace, run_dir), None, strategy, final_prompt
    raise ValueError(f"unsupported provider: {provider}")

def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_arm(
    *,
    repo: Path,
    case: dict[str, Any],
    provider: str,
    binary: str,
    model: str | None,
    mode: str,
    repetition: int,
    out_root: Path,
    campaign_id: str = "adhoc",
    suite_sha256: str = "adhoc-suite",
    enabled_skill_names: list[str] | None = None,
    timeout_seconds: int,
    max_budget_usd: float | None,
    command_json: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    case_id = str(case["id"])
    skill_name = str(case.get("skill") or "")
    if enabled_skill_names is None:
        enabled_skill_names = [] if mode == "control" else ([skill_name] if skill_name else [])
    enabled_skill_names = list(enabled_skill_names)
    evaluated_skill_names = list(case.get("evaluated_skills") or ([skill_name] if skill_name else enabled_skill_names))
    model_slug = "default" if not model else re.sub(r"[^A-Za-z0-9._-]+", "-", model).strip("-") or "model"
    run_dir = out_root / provider / model_slug / case_id / f"run-{repetition:03d}" / mode
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    workspace = run_dir / "workspace"
    if dry_run and case.get("git_fixture"):
        workspace.mkdir(parents=True)
    else:
        _copy_fixture(repo, case, workspace, run_dir)
    skill_pairs = [(name, repo / "skills" / name) for name in enabled_skill_names]
    prompt = str(case["request"])
    argv, extra_env, loading_strategy, final_prompt = _provider_invocation(
        provider=provider, binary=binary, model=model, prompt=prompt, enabled_skills=skill_pairs,
        workspace=workspace, run_dir=run_dir, max_budget_usd=max_budget_usd, command_json=command_json,
    )
    (run_dir / "prompt.txt").write_text(final_prompt + "\n", encoding="utf-8")
    _write_json(run_dir / "invocation.json", {"argv": argv, "loading_strategy": loading_strategy, "model": model})

    skill_hashes = {name: sha256_tree(repo / "skills" / name) for name in evaluated_skill_names}
    case_sha256 = sha256_json(case)
    base: dict[str, Any] = {
        "schema_version": 2,
        "campaign_id": campaign_id,
        "suite_sha256": suite_sha256,
        "case_sha256": case_sha256,
        "skill_hashes": skill_hashes,
        "skill_sha256": skill_hashes.get(skill_name) if len(skill_hashes) == 1 else None,
        "enabled_skills": enabled_skill_names,
        "evaluated_skills": evaluated_skill_names,
        "repo_version": repo_version(repo),
        "repo_commit": repo_git_head(repo),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "provider_version": command_version(binary) if provider != "command" else "custom-command",
        "model": model,
        "scenario_id": case_id,
        "skill": skill_name,
        "run": repetition,
        "mode": mode,
        "loading_strategy": loading_strategy,
        "pass_threshold": float(case.get("pass_threshold", 0.8)),
        "manual_checks": list(case.get("manual_checks", [])),
        **runtime_metadata(),
    }
    if dry_run:
        base.update({"status": "planned", "argv": argv})
        return base

    result = run_process(argv, cwd=workspace, timeout_seconds=timeout_seconds, env=extra_env)
    (run_dir / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(result.stderr, encoding="utf-8")
    trace, final_text = normalize_trace(result.stdout, result.stderr)
    (run_dir / "trace.txt").write_text(trace, encoding="utf-8")
    (run_dir / "final.txt").write_text(final_text, encoding="utf-8")
    changed_files = git_changed_files(workspace)
    _write_json(run_dir / "changed-files.json", changed_files)
    workflow_metrics = {
        **git_diff_metrics(workspace, changed_files, list(case.get("expected_change_globs", []))),
        **trace_workflow_metrics(result.stdout, result.stderr),
        "prompt_chars": len(final_prompt),
        "final_response_chars": len(final_text),
    }
    _write_json(run_dir / "workflow-metrics.json", workflow_metrics)
    grader_results, score, max_score, fraction = grade_case(
        list(case["graders"]),
        workspace=workspace,
        repo=repo,
        run_dir=run_dir,
        trace=trace,
        changed_files=changed_files,
    )
    status = "timeout" if result.timed_out else ("completed" if result.exit_code == 0 else "provider-error")
    base.update(
        {
            "status": status,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "duration_seconds": round(result.duration_seconds, 4),
            "usage": extract_usage(result.stdout),
            "workflow_metrics": workflow_metrics,
            "changed_files": changed_files,
            "grader_results": grader_results,
            "score": score,
            "max_score": max_score,
            "score_fraction": fraction,
            "passed": status == "completed" and fraction >= float(case.get("pass_threshold", 0.8)),
            "artifact_dir": str(run_dir),
        }
    )
    _write_json(run_dir / "result.json", base)
    return base


def _select_cases(cases: list[dict[str, Any]], requested: list[str]) -> list[dict[str, Any]]:
    if not requested:
        return cases
    wanted = set(requested)
    selected = [case for case in cases if str(case["id"]) in wanted]
    missing = sorted(wanted - {str(case["id"]) for case in selected})
    if missing:
        raise ValueError(f"unknown live eval case(s): {', '.join(missing)}")
    return selected


def validate_command(repo: Path, cases_path: Path) -> int:
    try:
        cases = load_live_cases(cases_path, repo)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] {len(cases)} live eval case(s) validated")
    return 0


def _campaign_id(provider: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{provider}-{uuid.uuid4().hex[:8]}"


def _arm_order(repetition: int, policy: str) -> tuple[str, str]:
    if policy == "control-first":
        return ("control", "treatment")
    if policy == "treatment-first":
        return ("treatment", "control")
    return ("control", "treatment") if repetition % 2 else ("treatment", "control")


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
        done.add((str(item.get("provider")), str(item.get("model") or "default"), str(item.get("scenario_id")), int(item.get("run", 0)), str(item.get("mode"))))
    return done


def run_command(args: argparse.Namespace, repo: Path, cases_path: Path) -> int:
    try:
        cases = _select_cases(load_live_cases(cases_path, repo), args.case)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
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
    records_path = out_root / f"{args.provider}-runs.jsonl"
    if args.resume and not args.campaign_id:
        print("[ERROR] --resume requires --campaign-id so evidence is not mixed across campaigns", file=sys.stderr)
        return 2
    campaign_id = args.campaign_id or _campaign_id(args.provider)
    if records_path.exists() and not args.append and not args.resume:
        records_path.unlink()
    completed = _completed_keys(records_path, campaign_id) if args.resume else set()
    suite_hash = sha256_file(cases_path)
    records: list[dict[str, Any]] = []
    for model in models:
        for case in cases:
            for repetition in range(1, args.runs + 1):
                for mode in _arm_order(repetition, args.arm_order):
                    key=(args.provider, str(model or "default"), str(case["id"]), repetition, mode)
                    if key in completed:
                        print(f"[SKIP] {case['id']} model={model or 'default'} run={repetition} mode={mode} campaign={campaign_id}")
                        continue
                    try:
                        record = _run_arm(
                            repo=repo, case=case, provider=args.provider, binary=binary, model=model,
                            mode=mode, repetition=repetition, out_root=out_root, campaign_id=campaign_id, suite_sha256=suite_hash,
                            timeout_seconds=args.timeout_seconds, max_budget_usd=args.max_budget_usd,
                            command_json=args.command_json, dry_run=args.dry_run,
                        )
                    except (OSError, ValueError, RuntimeError) as exc:
                        print(f"[ERROR] {case['id']} model={model or 'default'} run {repetition} {mode}: {exc}", file=sys.stderr)
                        return 1
                    records.append(record)
                    with records_path.open("a", encoding="utf-8", newline="\n") as handle:
                        handle.write(json.dumps(record, sort_keys=True) + "\n")
                    if args.dry_run:
                        print(f"[PLAN] {case['id']} model={model or 'default'} run={repetition} mode={mode} provider={args.provider}")
                    else:
                        print(f"[{'PASS' if record.get('passed') else 'FAIL'}] {case['id']} model={model or 'default'} run={repetition} mode={mode} score={record.get('score_fraction', 0):.3f}")
    print(f"[OK] Campaign {campaign_id}: wrote {len(records)} run record(s) to {records_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or validate live RED/GREEN skill evaluations.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate live-eval definitions and fixtures")
    validate.add_argument("--cases", type=Path, default=Path("evals/live-cases.json"))

    run = sub.add_parser("run", help="Execute control/treatment model runs")
    run.add_argument("--cases", type=Path, default=Path("evals/live-cases.json"))
    run.add_argument("--provider", choices=("codex", "claude", "command"), required=True)
    run.add_argument("--binary", default=None, help="Override codex/claude executable path")
    run.add_argument("--model", action="append", default=[], help="Model to evaluate; repeat to build a model matrix")
    run.add_argument("--runs", type=int, default=3)
    run.add_argument("--case", action="append", default=[], help="Run only this case ID; repeat as needed")
    run.add_argument("--timeout-seconds", type=int, default=900)
    run.add_argument("--max-budget-usd", type=float, default=None, help="Claude print-mode budget cap")
    run.add_argument("--output-dir", type=Path, default=Path(".verification/live-evals"))
    run.add_argument("--command-json", default=None, help="Provider=command argv JSON; supports {prompt}, {workspace}, {run_dir}")
    run.add_argument("--dry-run", action="store_true", help="Prepare fixtures/invocations without calling a model")
    run.add_argument("--append", action="store_true", help="Append to an existing provider runs JSONL instead of replacing it")
    run.add_argument("--campaign-id", default=None, help="Stable campaign identifier used for pairing/resume/provenance")
    run.add_argument("--resume", action="store_true", help="Skip completed arms from the same --campaign-id")
    run.add_argument("--arm-order", choices=("alternate", "control-first", "treatment-first"), default="alternate", help="Balance control/treatment ordering across repetitions")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    cases_path = args.cases if args.cases.is_absolute() else (repo / args.cases)
    if args.command == "validate":
        return validate_command(repo, cases_path)
    return run_command(args, repo, cases_path)


if __name__ == "__main__":
    sys.exit(main())
