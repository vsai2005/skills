#!/usr/bin/env python3
"""Run a command repeatedly and report observed failure/inconclusive rates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class RunResult:
    run: int
    exit_code: int | None
    duration_seconds: float
    outcome: str
    signature: str | None
    signature_excerpt: str | None = None
    stdout: str = ""
    stderr: str = ""
    stdout_log: str | None = None
    stderr_log: str | None = None

    @property
    def failed(self) -> bool:
        return self.outcome == "test-failure"

    @property
    def inconclusive(self) -> bool:
        return self.outcome in {"timeout", "infrastructure-error", "zero-tests"}


def _normalize_output(text: str) -> str:
    text = ANSI_RE.sub("", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-40:])


def _signature_material(stdout: str, stderr: str) -> str:
    out = _normalize_output(stdout)
    err = _normalize_output(stderr)
    parts: list[str] = []
    if out:
        parts.append(f"STDOUT:\n{out}")
    if err:
        parts.append(f"STDERR:\n{err}")
    return "\n".join(parts)


def failure_signature(stdout: str, stderr: str) -> str | None:
    material = _signature_material(stdout, stderr)
    if not material:
        return None
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def failure_excerpt(stdout: str, stderr: str, limit: int = 220) -> str | None:
    material = _signature_material(stdout, stderr)
    if not material:
        return None
    compact = " | ".join(material.splitlines())
    return compact[:limit] + ("…" if len(compact) > limit else "")


def _write_logs(log_dir: Path | None, run: int, stdout: str, stderr: str) -> tuple[str | None, str | None]:
    if log_dir is None:
        return None, None
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"run-{run:03d}.stdout.log"
    stderr_path = log_dir / f"run-{run:03d}.stderr.log"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return str(stdout_path), str(stderr_path)


def _popen_group_kwargs() -> dict[str, object]:
    if os.name == "posix":
        return {"start_new_session": True}
    if os.name == "nt":
        return {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
    return {}


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    """Best-effort termination of the timed-out command and its descendants."""
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=0.3)
            return
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return
    if os.name == "nt":
        # taskkill /T is the most reliable standard Windows facility for
        # descendants created by arbitrary test runners.
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    try:
        process.kill()
    except OSError:
        pass


def _run_once(command: list[str], cwd: Path | None, timeout: float | None) -> tuple[int | None, str, str, str]:
    process = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **_popen_group_kwargs(),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout or "", stderr or "", "completed"
    except subprocess.TimeoutExpired:
        _terminate_process_tree(process)
        stdout, stderr = process.communicate()
        return None, stdout or "", stderr or "", "timeout"


def run_repeated(
    command: list[str],
    runs: int,
    cwd: Path | None = None,
    *,
    timeout: float | None = None,
    require_output_regex: str | None = None,
    infrastructure_exit_codes: set[int] | None = None,
    zero_test_exit_codes: set[int] | None = None,
    log_dir: Path | None = None,
) -> list[RunResult]:
    if runs < 1:
        raise ValueError("runs must be at least 1")
    if not command:
        raise ValueError("command must not be empty")
    if timeout is not None and timeout <= 0:
        raise ValueError("timeout must be greater than zero")
    required = re.compile(require_output_regex) if require_output_regex else None
    infra_codes = infrastructure_exit_codes or set()
    zero_codes = zero_test_exit_codes or set()

    results: list[RunResult] = []
    for index in range(1, runs + 1):
        started = time.monotonic()
        exit_code, stdout, stderr, execution = _run_once(command, cwd, timeout)
        if execution == "timeout":
            outcome = "timeout"
        else:
            assert exit_code is not None
            combined = f"{stdout}\n{stderr}"
            if exit_code in zero_codes:
                outcome = "zero-tests"
            elif exit_code == 0 and required is not None and not required.search(combined):
                outcome = "zero-tests"
            elif exit_code == 0:
                outcome = "pass"
            elif exit_code in infra_codes:
                outcome = "infrastructure-error"
            else:
                outcome = "test-failure"

        duration = time.monotonic() - started
        stdout_log, stderr_log = _write_logs(log_dir, index, stdout, stderr)
        signature = failure_signature(stdout, stderr) if outcome != "pass" else None
        excerpt = failure_excerpt(stdout, stderr) if outcome != "pass" else None
        results.append(
            RunResult(
                run=index,
                exit_code=exit_code,
                duration_seconds=duration,
                outcome=outcome,
                signature=signature,
                signature_excerpt=excerpt,
                stdout=stdout,
                stderr=stderr,
                stdout_log=stdout_log,
                stderr_log=stderr_log,
            )
        )
    return results


def recommended_runs_for_detection(expected_rate: float, confidence: float = 0.95) -> int:
    """Return runs needed to observe >=1 failure with the requested probability.

    This assumes independent runs with a stable per-run failure probability. It is
    a planning heuristic, not proof that flaky tests are independent or stationary.
    """
    if not 0 < expected_rate < 1:
        raise ValueError("expected_rate must be between 0 and 1 (exclusive)")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1 (exclusive)")
    return max(1, math.ceil(math.log(1 - confidence) / math.log(1 - expected_rate)))


def wilson_interval(failures: int, total: int, z: float = 1.96) -> tuple[float, float] | None:
    if total <= 0:
        return None
    p = failures / total
    denom = 1 + (z * z / total)
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def summarize(results: list[RunResult]) -> dict[str, object]:
    failures = sum(result.outcome == "test-failure" for result in results)
    passes = sum(result.outcome == "pass" for result in results)
    timeouts = sum(result.outcome == "timeout" for result in results)
    infrastructure_errors = sum(result.outcome == "infrastructure-error" for result in results)
    zero_tests = sum(result.outcome == "zero-tests" for result in results)
    comparable = passes + failures
    rate = failures / comparable if comparable else 0.0
    interval = wilson_interval(failures, comparable)
    signatures: dict[str, dict[str, object]] = {}
    for result in results:
        if result.signature:
            bucket = signatures.setdefault(
                result.signature,
                {"count": 0, "excerpt": result.signature_excerpt or ""},
            )
            bucket["count"] = int(bucket["count"]) + 1
    return {
        "runs": len(results),
        "comparable_runs": comparable,
        "passes": passes,
        "failures": failures,
        "timeouts": timeouts,
        "infrastructure_errors": infrastructure_errors,
        "zero_tests": zero_tests,
        "inconclusive_runs": timeouts + infrastructure_errors + zero_tests,
        "failure_rate": rate,
        "failure_rate_percent": rate * 100.0,
        "failure_rate_95pct_interval": (
            [interval[0], interval[1]] if interval is not None else None
        ),
        "failure_signatures": signatures,
    }


def render_text(results: list[RunResult]) -> str:
    stats = summarize(results)
    interval = stats["failure_rate_95pct_interval"]
    interval_text = "n/a"
    if isinstance(interval, list):
        interval_text = f"{interval[0] * 100:.1f}%–{interval[1] * 100:.1f}%"
    lines = [
        f"Runs: {stats['runs']}",
        f"Comparable test runs: {stats['comparable_runs']}",
        f"Passes: {stats['passes']}",
        f"Test failures: {stats['failures']}",
        f"Inconclusive runs: {stats['inconclusive_runs']} "
        f"(timeouts {stats['timeouts']}, infrastructure {stats['infrastructure_errors']}, zero-tests {stats['zero_tests']})",
        f"Observed failure rate: {stats['failure_rate_percent']:.1f}%",
        f"95% Wilson interval: {interval_text}",
        "",
        "Per-run results:",
    ]
    for result in results:
        exit_text = "timeout" if result.exit_code is None else f"exit {result.exit_code}"
        sig = f", signature {result.signature}" if result.signature else ""
        lines.append(f"- {result.run}: {result.outcome.upper()} ({exit_text}, {result.duration_seconds:.3f}s{sig})")
        if result.signature_excerpt:
            lines.append(f"  - {result.signature_excerpt}")
    return "\n".join(lines)


def _json_result(result: RunResult) -> dict[str, object]:
    data = asdict(result)
    data["stdout"] = result.stdout[-4000:]
    data["stderr"] = result.stderr[-4000:]
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repeat a command N times and measure observed flaky-test behavior.")
    parser.add_argument("--runs", type=int, default=None, help="Number of repetitions. Default: 10, or the rate-based recommendation when --expected-rate is set")
    parser.add_argument("--expected-rate", type=float, default=None, help="Expected per-run failure probability as a fraction, e.g. 0.05 for 5%%; used to size N when --runs is omitted")
    parser.add_argument("--detection-confidence", type=float, default=0.95, help="Desired probability of observing at least one failure when --expected-rate is supplied (default: 0.95)")
    parser.add_argument("--cwd", type=Path, default=None, help="Working directory for the command")
    parser.add_argument("--timeout", type=float, default=None, help="Per-run timeout in seconds")
    parser.add_argument("--require-output-regex", default=None, help="Regex that must appear on successful runs; missing output is classified as zero-tests")
    parser.add_argument("--infrastructure-exit-code", action="append", type=int, default=[], help="Exit code that represents infrastructure failure rather than a test failure; repeat as needed")
    parser.add_argument("--zero-tests-exit-code", action="append", type=int, default=[], help="Exit code that means the runner selected zero tests; repeat as needed (for example pytest commonly uses 5)")
    parser.add_argument("--log-dir", type=Path, default=None, help="Write per-run stdout/stderr logs here")
    parser.add_argument("--json", action="store_true", help="Emit JSON only; child command output is captured")
    parser.add_argument("--allow-failures", action="store_true", help="Return zero when only test failures were observed")
    parser.add_argument("--allow-inconclusive", action="store_true", help="Return zero despite timeout/infrastructure/zero-test runs")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run; place it after --")
    args = parser.parse_args(argv)

    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    try:
        recommendation = (
            recommended_runs_for_detection(args.expected_rate, args.detection_confidence)
            if args.expected_rate is not None
            else None
        )
        runs = args.runs if args.runs is not None else (recommendation or 10)
        results = run_repeated(
            command,
            runs,
            args.cwd,
            timeout=args.timeout,
            require_output_regex=args.require_output_regex,
            infrastructure_exit_codes=set(args.infrastructure_exit_code),
            zero_test_exit_codes=set(args.zero_tests_exit_code),
            log_dir=args.log_dir,
        )
    except (ValueError, OSError, re.error) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    stats = summarize(results)
    planning = {
        "expected_rate": args.expected_rate,
        "detection_confidence": args.detection_confidence if args.expected_rate is not None else None,
        "recommended_runs": recommendation,
        "planned_runs": runs,
        "meets_recommendation": (runs >= recommendation) if recommendation is not None else None,
    }
    if args.json:
        print(json.dumps({"planning": planning, "summary": stats, "results": [_json_result(result) for result in results]}, indent=2))
    else:
        if recommendation is not None:
            print(
                f"Rate-based planning: expected {args.expected_rate * 100:.2f}% failure rate, "
                f"{args.detection_confidence * 100:.1f}% detection confidence -> "
                f"recommended N={recommendation}; running N={runs}"
            )
        print(render_text(results))

    if stats["inconclusive_runs"] and not args.allow_inconclusive:
        return 2
    if stats["failures"] and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
