#!/usr/bin/env python3
"""Retain and page verification stdout/stderr without flooding active context."""

from __future__ import annotations

import hashlib
import re
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

SAFE_EVIDENCE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
MAX_VIEW_LINES = 200
FAILURE_PREVIEW_LINES = 12
FAILURE_PREVIEW_BYTES = 8192
FAILURE_PREVIEW_CHARS = 1600


def validate_evidence_id(evidence_id: str) -> str:
    if not SAFE_EVIDENCE_ID_RE.fullmatch(evidence_id):
        raise ValueError(
            "evidence id must be 1-128 characters using letters, digits, '.', '_' or '-' "
            "and must start with a letter or digit"
        )
    return evidence_id


def prepare_capture_paths(artifact_root: Path, evidence_id: str) -> dict[str, Path]:
    """Create one confined artifact directory and return stdout/stderr paths."""
    validate_evidence_id(evidence_id)
    root = artifact_root.resolve()
    run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    run_dir = root / evidence_id / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    return {
        "artifact_root": root,
        "artifact_dir": run_dir,
        "stdout": run_dir / "stdout.log",
        "stderr": run_dir / "stderr.log",
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count(path: Path) -> int:
    count = 0
    last = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            count += chunk.count(b"\n")
            last = chunk[-1:] if chunk else last
    if path.stat().st_size and last != b"\n":
        count += 1
    return count


def _artifact_metadata(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "sha256": _sha256_file(path),
        "bytes": path.stat().st_size,
        "lines": _line_count(path),
    }


def describe_captured_output(paths: dict[str, Path]) -> dict[str, object]:
    """Return durable metadata after a command has written its capture files."""
    return {
        "artifact_root": str(paths["artifact_root"]),
        "artifact_dir": str(paths["artifact_dir"]),
        "stdout_artifact": _artifact_metadata(paths["stdout"]),
        "stderr_artifact": _artifact_metadata(paths["stderr"]),
    }


def _latest_artifact_event(
    events: list[dict[str, object]], evidence_id: str
) -> dict[str, object] | None:
    validate_evidence_id(evidence_id)
    for event in reversed(events):
        if (
            str(event.get("id")) == evidence_id
            and event.get("event") == "run"
            and event.get("capture_output") is True
        ):
            return event
    return None


def _tail_bytes(path: Path, limit: int = FAILURE_PREVIEW_BYTES) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size > limit:
            handle.seek(-limit, 2)
        return handle.read()


def failure_excerpt(paths: dict[str, Path]) -> str:
    """Return a bounded failure-first excerpt, preferring stderr."""
    source = paths["stderr"] if paths["stderr"].stat().st_size else paths["stdout"]
    if not source.exists() or source.stat().st_size == 0:
        return ""
    text = _tail_bytes(source).decode("utf-8", "replace")
    lines = text.splitlines()
    excerpt = "\n".join(lines[-FAILURE_PREVIEW_LINES:])
    if len(excerpt) > FAILURE_PREVIEW_CHARS:
        excerpt = "…" + excerpt[-(FAILURE_PREVIEW_CHARS - 1) :]
    return excerpt


def render_capture_summary(event: dict[str, object]) -> str:
    stdout_meta = event.get("stdout_artifact")
    stderr_meta = event.get("stderr_artifact")
    stdout_meta = stdout_meta if isinstance(stdout_meta, dict) else {}
    stderr_meta = stderr_meta if isinstance(stderr_meta, dict) else {}
    duration = event.get("duration_seconds")
    duration_text = f"{float(duration):.3f}s" if isinstance(duration, (int, float)) else "n/a"
    summary = (
        f"{event.get('id')} {event.get('label')}: exit {event.get('exit_code')} in {duration_text}; "
        f"stdout {stdout_meta.get('bytes', 0)} B/{stdout_meta.get('lines', 0)} lines; "
        f"stderr {stderr_meta.get('bytes', 0)} B/{stderr_meta.get('lines', 0)} lines; "
        f"full evidence: {event.get('artifact_dir')}"
    )
    excerpt = str(event.get("failure_excerpt") or "").strip()
    if event.get("exit_code") not in (None, 0) and excerpt:
        summary += "\nfailure excerpt:\n" + excerpt
    return summary


def _confined_artifact_path(
    meta: dict[str, object],
    *,
    artifact_root: Path,
    expected_name: str,
) -> Path:
    raw = meta.get("path")
    if not raw:
        raise ValueError("captured artifact path is missing")
    root = artifact_root.resolve()
    path = Path(str(raw)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"captured artifact escapes allowed root: {path}") from exc
    if path.name != expected_name:
        raise ValueError(
            f"captured artifact has unexpected filename {path.name!r}; expected {expected_name!r}"
        )
    return path


def _verify_artifact(path: Path, meta: dict[str, object]) -> None:
    if not path.is_file():
        raise ValueError(f"retained artifact is missing: {path}")
    expected = str(meta.get("sha256") or "")
    if not expected:
        raise ValueError(f"retained artifact has no recorded digest: {path}")
    actual = _sha256_file(path)
    if actual != expected:
        raise ValueError(
            f"retained artifact digest mismatch: {path} ({actual} != {expected})"
        )
    expected_bytes = meta.get("bytes")
    if isinstance(expected_bytes, int) and path.stat().st_size != expected_bytes:
        raise ValueError(
            f"retained artifact size mismatch: {path} "
            f"({path.stat().st_size} != {expected_bytes})"
        )


def _read_range(path: Path, start_line: int, line_count: int) -> list[str]:
    selected: list[str] = []
    end_line = start_line + line_count
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            if number < start_line:
                continue
            if number >= end_line:
                break
            selected.append(line.rstrip("\r\n"))
    return selected


def _read_tail(path: Path, count: int) -> list[str]:
    lines: deque[str] = deque(maxlen=count)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            lines.append(line.rstrip("\r\n"))
    return list(lines)


def view_captured_output(
    events: list[dict[str, object]],
    evidence_id: str,
    *,
    stream: str,
    artifact_root: Path,
    start_line: int = 1,
    line_count: int = 80,
    tail: int | None = None,
) -> str:
    if line_count < 1 or line_count > MAX_VIEW_LINES:
        raise ValueError(f"--line-count must be between 1 and {MAX_VIEW_LINES}")
    if start_line < 1:
        raise ValueError("--start-line must be at least 1")
    if tail is not None and (tail < 1 or tail > MAX_VIEW_LINES):
        raise ValueError(f"--tail must be between 1 and {MAX_VIEW_LINES}")

    event = _latest_artifact_event(events, evidence_id)
    if event is None:
        raise ValueError(f"no captured output found for evidence id {evidence_id}")

    meta = event.get(f"{stream}_artifact")
    if not isinstance(meta, dict):
        raise ValueError(f"{stream} artifact is unavailable for evidence id {evidence_id}")

    path = _confined_artifact_path(
        meta,
        artifact_root=artifact_root,
        expected_name=f"{stream}.log",
    )
    _verify_artifact(path, meta)

    total_lines = meta.get("lines")
    total = int(total_lines) if isinstance(total_lines, int) else _line_count(path)
    if tail is not None:
        selected = _read_tail(path, tail)
        first = max(1, total - len(selected) + 1)
    else:
        first = start_line
        selected = _read_range(path, start_line, line_count)

    last = first + len(selected) - 1 if selected else first - 1
    header = (
        f"[{evidence_id} {stream} lines {first}-{last} of {total}; "
        f"sha256 {meta.get('sha256', 'unknown')}]"
    )
    return header + ("\n" + "\n".join(selected) if selected else "\n<no lines>")
