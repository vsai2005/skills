#!/usr/bin/env python3
"""Retain and page verification stdout/stderr without flooding active context."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _artifact_metadata(path: Path, data: bytes) -> dict[str, object]:
    text = data.decode("utf-8", "replace")
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "lines": len(text.splitlines()),
    }


def write_captured_output(
    artifact_root: Path,
    evidence_id: str,
    stdout: bytes,
    stderr: bytes,
) -> dict[str, object]:
    run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    run_dir = artifact_root.resolve() / evidence_id / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    return {
        "artifact_dir": str(run_dir),
        "stdout_artifact": _artifact_metadata(stdout_path, stdout),
        "stderr_artifact": _artifact_metadata(stderr_path, stderr),
    }


def _latest_artifact_event(
    events: list[dict[str, object]], evidence_id: str
) -> dict[str, object] | None:
    for event in reversed(events):
        if (
            str(event.get("id")) == evidence_id
            and event.get("event") == "run"
            and event.get("capture_output") is True
        ):
            return event
    return None


def render_capture_summary(event: dict[str, object]) -> str:
    stdout_meta = event.get("stdout_artifact")
    stderr_meta = event.get("stderr_artifact")
    stdout_meta = stdout_meta if isinstance(stdout_meta, dict) else {}
    stderr_meta = stderr_meta if isinstance(stderr_meta, dict) else {}
    duration = event.get("duration_seconds")
    duration_text = f"{float(duration):.3f}s" if isinstance(duration, (int, float)) else "n/a"
    return (
        f"{event.get('id')} {event.get('label')}: exit {event.get('exit_code')} in {duration_text}; "
        f"stdout {stdout_meta.get('bytes', 0)} B/{stdout_meta.get('lines', 0)} lines; "
        f"stderr {stderr_meta.get('bytes', 0)} B/{stderr_meta.get('lines', 0)} lines; "
        f"full evidence: {event.get('artifact_dir')}"
    )


def view_captured_output(
    events: list[dict[str, object]],
    evidence_id: str,
    *,
    stream: str,
    start_line: int = 1,
    line_count: int = 80,
    tail: int | None = None,
) -> str:
    if line_count < 1 or line_count > 200:
        raise ValueError("--line-count must be between 1 and 200")
    if start_line < 1:
        raise ValueError("--start-line must be at least 1")
    if tail is not None and (tail < 1 or tail > 200):
        raise ValueError("--tail must be between 1 and 200")

    event = _latest_artifact_event(events, evidence_id)
    if event is None:
        raise ValueError(f"no captured output found for evidence id {evidence_id}")

    meta = event.get(f"{stream}_artifact")
    if not isinstance(meta, dict) or not meta.get("path"):
        raise ValueError(f"{stream} artifact is unavailable for evidence id {evidence_id}")

    path = Path(str(meta["path"]))
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read retained artifact {path}: {exc}") from exc

    if tail is not None:
        selected = lines[-tail:]
        first = max(1, len(lines) - len(selected) + 1)
    else:
        first = start_line
        selected = lines[start_line - 1 : start_line - 1 + line_count]

    last = first + len(selected) - 1 if selected else first - 1
    header = (
        f"[{evidence_id} {stream} lines {first}-{last} of {len(lines)}; "
        f"sha256 {meta.get('sha256', 'unknown')}]"
    )
    return header + ("\n" + "\n".join(selected) if selected else "\n<no lines>")
