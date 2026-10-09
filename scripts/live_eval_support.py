#!/usr/bin/env python3
"""Shared helpers for live RED/GREEN skill evaluations.

The helpers deliberately use only the Python standard library. They keep model
execution isolated from grading and retain raw traces so a failed grade can be
inspected rather than reduced to one opaque score.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any





ALLOWED_GRADER_TYPES = {
    "command",
    "file_exists",
    "file_contains",
    "file_not_contains",
    "file_regex",
    "file_regex_absent",
    "trace_regex",
    "trace_regex_absent",
    "changed_files_max",
    "changed_files_min",
    "file_line_max",
    "file_line_min",
}


@dataclass(frozen=True)
class ProcessResult:
    argv: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool


def load_live_cases(path: Path, root: Path | None = None) -> list[dict[str, Any]]:
    """Load and validate live-eval case definitions."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load live evals: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError("live evals must be a non-empty JSON list")

    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            raise ValueError(f"live eval case {index} must be an object")
        case_id = str(case.get("id", "")).strip()
        skill = str(case.get("skill", "")).strip()
        fixture = str(case.get("fixture", "")).strip()
        git_fixture = case.get("git_fixture")
        request = str(case.get("request", "")).strip()
        if not case_id or case_id in seen:
            raise ValueError(f"live eval case {index} has missing/duplicate id: {case_id!r}")
        seen.add(case_id)
        if not skill or not request:
            raise ValueError(f"live eval case {case_id} must define skill and request")
        if bool(fixture) == bool(git_fixture):
            raise ValueError(f"live eval case {case_id} must define exactly one of fixture or git_fixture")
        if git_fixture is not None:
            if not isinstance(git_fixture, dict):
                raise ValueError(f"live eval case {case_id} git_fixture must be an object")
            repo_url = str(git_fixture.get("repo_url", "")).strip()
            base_commit = str(git_fixture.get("base_commit", "")).strip()
            if not repo_url.startswith("https://github.com/") or repo_url.count("@"):
                raise ValueError(f"live eval case {case_id} git_fixture repo_url must be a credential-free GitHub HTTPS URL")
            if not re.fullmatch(r"[0-9a-fA-F]{40}", base_commit):
                raise ValueError(f"live eval case {case_id} git_fixture base_commit must be a 40-hex commit")
        threshold = case.get("pass_threshold", 0.8)
        if not isinstance(threshold, (int, float)) or not 0 <= float(threshold) <= 1:
            raise ValueError(f"live eval case {case_id} has invalid pass_threshold")
        graders = case.get("graders")
        if not isinstance(graders, list) or not graders:
            raise ValueError(f"live eval case {case_id} must define one or more graders")
        grader_ids: set[str] = set()
        for grader_index, grader in enumerate(graders):
            if not isinstance(grader, dict):
                raise ValueError(f"live eval case {case_id} grader {grader_index} must be an object")
            grader_id = str(grader.get("id", "")).strip()
            grader_type = str(grader.get("type", "")).strip()
            weight = grader.get("weight", 1)
            if not grader_id or grader_id in grader_ids:
                raise ValueError(f"live eval case {case_id} has missing/duplicate grader id: {grader_id!r}")
            grader_ids.add(grader_id)
            if grader_type not in ALLOWED_GRADER_TYPES:
                raise ValueError(f"live eval case {case_id} grader {grader_id} has unknown type {grader_type!r}")
            if not isinstance(weight, (int, float)) or float(weight) <= 0:
                raise ValueError(f"live eval case {case_id} grader {grader_id} must have positive weight")
            if grader_type == "command":
                argv = grader.get("argv")
                if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
                    raise ValueError(f"live eval case {case_id} grader {grader_id} command needs argv")
        setup = case.get("setup", [])
        if not isinstance(setup, list) or not all(
            isinstance(command, list) and command and all(isinstance(x, str) and x for x in command)
            for command in setup
        ):
            raise ValueError(f"live eval case {case_id} setup must be a list of argv lists")
        manual = case.get("manual_checks", [])
        if not isinstance(manual, list) or not all(isinstance(x, str) and x.strip() for x in manual):
            raise ValueError(f"live eval case {case_id} manual_checks must be strings")
        expected_globs = case.get("expected_change_globs", [])
        if not isinstance(expected_globs, list) or not all(isinstance(x, str) and x.strip() for x in expected_globs):
            raise ValueError(f"live eval case {case_id} expected_change_globs must be strings")
        if root is not None:
            if fixture:
                fixture_path = (root / fixture).resolve()
                try:
                    fixture_path.relative_to(root.resolve())
                except ValueError as exc:
                    raise ValueError(f"live eval case {case_id} fixture escapes repository") from exc
                if not fixture_path.is_dir():
                    raise ValueError(f"live eval case {case_id} fixture missing: {fixture}")
            skill_path = root / "skills" / skill / "SKILL.md"
            if not skill_path.is_file():
                raise ValueError(f"live eval case {case_id} names missing skill: {skill}")
        result.append(case)
    return result


def expand_argv(argv: list[str], *, workspace: Path, repo: Path, run_dir: Path) -> list[str]:
    mapping = {
        "{workspace}": str(workspace),
        "{repo}": str(repo),
        "{run_dir}": str(run_dir),
    }
    expanded: list[str] = []
    for value in argv:
        for token, replacement in mapping.items():
            value = value.replace(token, replacement)
        expanded.append(value)
    return expanded


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
    except (OSError, ProcessLookupError):
        try:
            process.kill()
        except OSError:
            pass


def run_process(
    argv: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> ProcessResult:
    """Run a child process with captured output and whole-process-tree timeout cleanup."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=(os.name != "nt"),
        creationflags=creationflags,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_tree(process)
        stdout, stderr = process.communicate()
    duration = time.monotonic() - started
    return ProcessResult(
        argv=list(argv),
        exit_code=process.returncode,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        timed_out=timed_out,
    )


def command_version(binary: str) -> str | None:
    path = shutil.which(binary)
    if not path:
        return None
    for args in ([path, "--version"], [path, "version"]):
        try:
            result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        text = (result.stdout or result.stderr).strip()
        if text:
            return text.splitlines()[0][:300]
    return path


def build_codex_command(binary: str, prompt: str, model: str | None = None) -> list[str]:
    argv = [binary, "exec", "--json", "--full-auto"]
    if model:
        argv += ["--model", model]
    argv.append(prompt)
    return argv


def build_claude_command(
    binary: str,
    prompt: str,
    *,
    plugin_dir: Path | None,
    control: bool,
    model: str | None = None,
    max_budget_usd: float | None = None,
) -> list[str]:
    argv = [
        binary,
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        "acceptEdits",
        "--no-session-persistence",
    ]
    if control:
        argv.append("--disable-slash-commands")
    if plugin_dir is not None:
        argv += ["--plugin-dir", str(plugin_dir)]
    if model:
        argv += ["--model", model]
    if max_budget_usd is not None:
        argv += ["--max-budget-usd", str(max_budget_usd)]
    argv.append(prompt)
    return argv


def copy_skill_readonly(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    if os.name != "nt":
        for path in sorted(destination.rglob("*"), reverse=True):
            try:
                path.chmod(0o555 if path.is_dir() else 0o444)
            except OSError:
                pass
        destination.chmod(0o555)


def prepare_prompt_skills(workspace: Path, skills: list[tuple[str, Path]]) -> tuple[list[Path], str]:
    targets: list[Path] = []
    lines = ["Reusable engineering skills are mounted for this evaluation."]
    for skill_name, skill_dir in skills:
        target = workspace / ".eval-skill" / skill_name
        target.parent.mkdir(parents=True, exist_ok=True)
        copy_skill_readonly(skill_dir, target)
        targets.append(target)
        lines.append(f"- {target.relative_to(workspace).as_posix()}/SKILL.md")
    lines.append("Before changing files, read the listed SKILL.md files and apply only the relevant workflows. Load only referenced files needed for the task.")
    return targets, "\n".join(lines)


def prepare_prompt_skill(workspace: Path, skill_dir: Path, skill_name: str) -> tuple[Path, str]:
    targets, instruction = prepare_prompt_skills(workspace, [(skill_name, skill_dir)])
    return targets[0], instruction


def prepare_claude_plugin_skills(run_dir: Path, skills: list[tuple[str, Path]]) -> Path:
    plugin = run_dir / "claude-plugin"
    (plugin / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    names = [name for name, _ in skills]
    slug = "-".join(names)[:80] or "control"
    manifest = {
        "name": f"engineering-quality-eval-{slug}",
        "version": "0.0.0",
        "description": f"Isolated live-eval plugin for {', '.join(names)}.",
    }
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for skill_name, skill_dir in skills:
        copy_skill_readonly(skill_dir, plugin / "skills" / skill_name)
    return plugin


def prepare_claude_plugin(run_dir: Path, skill_dir: Path, skill_name: str) -> Path:
    return prepare_claude_plugin_skills(run_dir, [(skill_name, skill_dir)])


def _collect_text(value: Any, out: list[str]) -> None:
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"text", "result", "message", "command", "cmd", "content", "output"}:
                _collect_text(item, out)
            elif isinstance(item, (dict, list)):
                _collect_text(item, out)
    elif isinstance(value, list):
        for item in value:
            _collect_text(item, out)


def normalize_trace(stdout: str, stderr: str) -> tuple[str, str]:
    """Return searchable trace text and a best-effort final textual response."""
    trace_parts: list[str] = []
    final_candidates: list[str] = []
    for raw in stdout.splitlines():
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            trace_parts.append(raw)
            final_candidates.append(raw)
            continue
        texts: list[str] = []
        _collect_text(value, texts)
        trace_parts.extend(texts)
        if isinstance(value, dict) and value.get("type") in {"result", "item.completed", "message"}:
            final_candidates.extend(texts)
    if stderr.strip():
        trace_parts.append(stderr)
    trace = "\n".join(trace_parts)
    final = final_candidates[-1] if final_candidates else ""
    return trace, final


def extract_usage(stdout: str) -> dict[str, int | float]:
    """Best-effort usage extraction without depending on one provider schema."""
    maxima: dict[str, int | float] = {}
    interesting = {
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "cache_read_input_tokens",
        "cache_creation_input_tokens",
        "total_cost_usd",
        "cost_usd",
        "duration_ms",
    }

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in interesting and isinstance(item, (int, float)) and not isinstance(item, bool):
                    current = maxima.get(key)
                    if current is None or item > current:
                        maxima[key] = item
                elif isinstance(item, (dict, list)):
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for raw in stdout.splitlines():
        try:
            visit(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return maxima


def git_changed_files(workspace: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(workspace), "status", "--porcelain=v1", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    paths: set[str] = set()
    fields = [part for part in result.stdout.split(b"\0") if part]
    for field in fields:
        text = field.decode("utf-8", "surrogateescape")
        if len(text) < 4:
            continue
        path = text[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith(".eval-skill/"):
            continue
        paths.add(path)
    return sorted(paths)



def git_diff_metrics(workspace: Path, changed_files: list[str], expected_globs: list[str] | None = None) -> dict[str, int | None]:
    """Return deterministic scope/churn metrics for the final workspace."""
    result = subprocess.run(
        ["git", "-C", str(workspace), "diff", "--numstat", "HEAD"],
        capture_output=True, text=True, check=False, encoding="utf-8",
    )
    churn = 0
    if result.returncode == 0:
        for raw in result.stdout.splitlines():
            parts = raw.split("\t", 2)
            if len(parts) == 3:
                for value in parts[:2]:
                    if value.isdigit():
                        churn += int(value)
    tracked = set()
    if result.returncode == 0:
        for raw in result.stdout.splitlines():
            parts = raw.split("\t", 2)
            if len(parts) == 3:
                tracked.add(parts[2])
    for rel in changed_files:
        if rel in tracked:
            continue
        path = workspace / rel
        if path.is_file():
            try:
                churn += len(path.read_text(encoding="utf-8").splitlines())
            except (OSError, UnicodeError):
                pass
    unrelated: int | None = None
    if expected_globs:
        unrelated = sum(1 for rel in changed_files if not any(fnmatch.fnmatch(rel, pat) for pat in expected_globs))
    return {
        "changed_file_count": len(changed_files),
        "diff_churn": churn,
        "unrelated_file_count": unrelated,
    }


def trace_workflow_metrics(stdout: str, stderr: str) -> dict[str, int]:
    """Best-effort process metrics derived from retained structured/raw traces.

    These are workflow signals, not universal quality scores. Raw traces remain the
    source of truth when a provider changes its event schema.
    """
    tool_events = 0
    clarification_events = 0
    repair_signals = 0
    read_paths: list[str] = []
    path_re = re.compile(r"(?:path|file(?:name)?)\s*[=:]\s*[\"']?([^\"'\s,}]+)", re.IGNORECASE)
    for raw in stdout.splitlines():
        lower = raw.lower()
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            item = None
        serialized = json.dumps(item, sort_keys=True).lower() if item is not None else lower
        if any(token in serialized for token in ('"tool"', 'tool_call', 'command_execution', 'shell_command', 'function_call')):
            tool_events += 1
        if any(token in serialized for token in ('ask_user', 'request_user_input', 'clarification')):
            clarification_events += 1
        if any(token in lower for token in ('test failed', 'tests failed', 'assertionerror', ' failed')):
            repair_signals += 1
        if any(token in serialized for token in ('read_file', 'open_file', 'readfile')):
            match = path_re.search(raw)
            if match:
                read_paths.append(match.group(1))
    repeated_reads = sum(max(0, count - 1) for count in {p: read_paths.count(p) for p in set(read_paths)}.values())
    return {
        "tool_event_count": tool_events,
        "clarification_event_count": clarification_events,
        "repair_signal_count": repair_signals,
        "repeated_file_read_count": repeated_reads,
    }
