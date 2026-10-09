#!/usr/bin/env python3
"""Deterministic graders for live skill-evaluation workspaces."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

try:
    from scripts.live_eval_support import expand_argv, run_process
except ModuleNotFoundError:
    from live_eval_support import expand_argv, run_process


@dataclass(frozen=True)
class GradeResult:
    id: str
    type: str
    passed: bool
    weight: float
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_file(workspace: Path, rel: str) -> Path:
    path = (workspace / rel).resolve()
    try:
        path.relative_to(workspace.resolve())
    except ValueError as exc:
        raise ValueError(f"grader path escapes workspace: {rel}") from exc
    return path


def _regex(pattern: str, text: str, ignore_case: bool) -> bool:
    flags = re.MULTILINE | (re.IGNORECASE if ignore_case else 0)
    return re.search(pattern, text, flags) is not None


def grade_one(
    grader: dict[str, Any],
    *,
    workspace: Path,
    repo: Path,
    run_dir: Path,
    trace: str,
    changed_files: list[str],
) -> GradeResult:
    grader_id = str(grader["id"])
    grader_type = str(grader["type"])
    weight = float(grader.get("weight", 1))
    ignore_case = bool(grader.get("ignore_case", True))

    if grader_type == "command":
        argv = expand_argv(list(grader["argv"]), workspace=workspace, repo=repo, run_dir=run_dir)
        timeout = int(grader.get("timeout_seconds", 60))
        expected_exit = int(grader.get("expected_exit", 0))
        result = run_process(argv, cwd=workspace, timeout_seconds=timeout)
        passed = (not result.timed_out) and result.exit_code == expected_exit
        detail = (
            f"exit={result.exit_code}, expected={expected_exit}, timeout={result.timed_out}; "
            f"stdout={result.stdout[-500:]!r}; stderr={result.stderr[-500:]!r}"
        )
        return GradeResult(grader_id, grader_type, passed, weight, detail)

    if grader_type in {"file_exists", "file_contains", "file_not_contains", "file_regex", "file_regex_absent", "file_line_max", "file_line_min"}:
        rel = str(grader.get("path", ""))
        target = _safe_file(workspace, rel)
        exists = target.is_file()
        if grader_type == "file_exists":
            return GradeResult(grader_id, grader_type, exists, weight, f"{rel} exists={exists}")
        if not exists:
            return GradeResult(grader_id, grader_type, False, weight, f"missing file: {rel}")
        text = target.read_text(encoding="utf-8", errors="replace")
        if grader_type == "file_contains":
            needle = str(grader.get("text", ""))
            passed = needle in text
            return GradeResult(grader_id, grader_type, passed, weight, f"contains {needle!r}={passed}")
        if grader_type == "file_not_contains":
            needle = str(grader.get("text", ""))
            passed = needle not in text
            return GradeResult(grader_id, grader_type, passed, weight, f"absent {needle!r}={passed}")
        if grader_type in {"file_regex", "file_regex_absent"}:
            pattern = str(grader.get("pattern", ""))
            matched = _regex(pattern, text, ignore_case)
            passed = matched if grader_type == "file_regex" else not matched
            return GradeResult(grader_id, grader_type, passed, weight, f"pattern {pattern!r}, matched={matched}")
        lines = len(text.splitlines())
        limit = int(grader.get("lines", 0))
        passed = lines <= limit if grader_type == "file_line_max" else lines >= limit
        return GradeResult(grader_id, grader_type, passed, weight, f"lines={lines}, threshold={limit}")

    if grader_type in {"trace_regex", "trace_regex_absent"}:
        pattern = str(grader.get("pattern", ""))
        matched = _regex(pattern, trace, ignore_case)
        passed = matched if grader_type == "trace_regex" else not matched
        return GradeResult(grader_id, grader_type, passed, weight, f"trace pattern {pattern!r}, matched={matched}")

    if grader_type in {"changed_files_max", "changed_files_min"}:
        count = len(changed_files)
        limit = int(grader.get("count", 0))
        passed = count <= limit if grader_type == "changed_files_max" else count >= limit
        return GradeResult(grader_id, grader_type, passed, weight, f"changed_files={count}, threshold={limit}")

    raise ValueError(f"unsupported grader type: {grader_type}")


def grade_case(
    graders: list[dict[str, Any]],
    *,
    workspace: Path,
    repo: Path,
    run_dir: Path,
    trace: str,
    changed_files: list[str],
) -> tuple[list[dict[str, Any]], float, float, float]:
    results = [
        grade_one(
            grader,
            workspace=workspace,
            repo=repo,
            run_dir=run_dir,
            trace=trace,
            changed_files=changed_files,
        )
        for grader in graders
    ]
    max_score = sum(item.weight for item in results)
    score = sum(item.weight for item in results if item.passed)
    fraction = score / max_score if max_score else 0.0
    return [item.as_dict() for item in results], score, max_score, fraction
