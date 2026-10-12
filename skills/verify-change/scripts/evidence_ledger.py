#!/usr/bin/env python3
"""Record verification commands and render evidence-based completion sections.

Locally executed evidence is trustworthy only when it can be bound to a Git
candidate state, the executed command matches any existing plan for its ID, and
the verification command does not mutate that candidate state unless the caller
explicitly allows state changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER = Path(".verification/evidence.jsonl")


@dataclass(frozen=True)
class RepoSnapshot:
    repo_root: str | None
    git_head: str | None
    state_fingerprint: str | None


@dataclass(frozen=True)
class EvidenceState:
    id: str
    label: str
    command: str
    status: str
    timestamp: str
    exit_code: int | None = None
    duration_seconds: float | None = None
    source: str = "planned"
    cwd: str | None = None
    repo_root: str | None = None
    git_head: str | None = None
    state_fingerprint: str | None = None
    state_changed_during_run: bool = False
    allow_state_change: bool = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _is_state_excluded(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    return normalized == "PENDING_TESTS.md" or normalized == ".verification" or normalized.startswith(".verification/")


def repository_snapshot(cwd: Path | None = None) -> RepoSnapshot:
    """Return a content-sensitive Git snapshot for the current candidate state.

    Verification bookkeeping is excluded so writing the ledger itself does not
    stale otherwise valid code evidence.
    """
    base = (cwd or Path.cwd()).resolve()
    root_result = _run_git(base, ["rev-parse", "--show-toplevel"])
    if root_result.returncode != 0:
        return RepoSnapshot(None, None, None)

    repo_root = Path(root_result.stdout.decode("utf-8", "replace").strip()).resolve()
    head_result = _run_git(repo_root, ["rev-parse", "HEAD"])
    git_head = head_result.stdout.decode("utf-8", "replace").strip() if head_result.returncode == 0 else None

    digest = hashlib.sha256()
    diff_result = _run_git(
        repo_root,
        [
            "diff",
            "--binary",
            "HEAD",
            "--",
            ".",
            ":(exclude).verification/**",
            ":(exclude)PENDING_TESTS.md",
        ],
    )
    if diff_result.returncode != 0:
        return RepoSnapshot(str(repo_root), git_head, None)
    digest.update(diff_result.stdout)

    untracked_result = _run_git(repo_root, ["ls-files", "--others", "--exclude-standard", "-z"])
    if untracked_result.returncode != 0:
        return RepoSnapshot(str(repo_root), git_head, None)
    for raw in sorted(item for item in untracked_result.stdout.split(b"\0") if item):
        rel = raw.decode("utf-8", "surrogateescape")
        if _is_state_excluded(rel):
            continue
        digest.update(b"U\0")
        digest.update(raw)
        digest.update(b"\0")
        try:
            digest.update((repo_root / rel).read_bytes())
        except OSError:
            digest.update(b"<unreadable>")
        digest.update(b"\0")

    return RepoSnapshot(str(repo_root), git_head, digest.hexdigest())


def append_event(path: Path, event: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def load_events(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    events: list[dict[str, object]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read ledger {path}: {exc}") from exc
    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at {path}:{lineno}: {exc}") from exc
        if not isinstance(data, dict) or not data.get("id") or not data.get("event"):
            raise ValueError(f"invalid ledger event at {path}:{lineno}")
        events.append(data)
    return events


def _event_snapshot(event: dict[str, object]) -> RepoSnapshot:
    return RepoSnapshot(
        str(event["repo_root"]) if event.get("repo_root") else None,
        str(event["git_head"]) if event.get("git_head") else None,
        str(event["state_fingerprint"]) if event.get("state_fingerprint") else None,
    )


def _snapshot_is_stale(recorded: RepoSnapshot, current: RepoSnapshot | None) -> bool:
    if current is None or not recorded.repo_root or not recorded.state_fingerprint:
        return False
    if not current.repo_root or not current.state_fingerprint:
        return True
    return (
        Path(recorded.repo_root).resolve() != Path(current.repo_root).resolve()
        or recorded.git_head != current.git_head
        or recorded.state_fingerprint != current.state_fingerprint
    )


def _canonical_command(command: str) -> tuple[str, ...]:
    """Canonicalize command text while preserving Windows backslashes."""
    windows_path = re.search(r"(?:^|[\s\"\'])[A-Za-z]:\\", command) is not None
    try:
        parts = shlex.split(command, posix=not windows_path)
    except ValueError:
        return tuple(command.split())
    if windows_path:
        parts = [
            part[1:-1]
            if len(part) >= 2 and part[0] == part[-1] and part[0] in {"'", '"'}
            else part
            for part in parts
        ]
    return tuple(parts)


def _known_command(events: list[dict[str, object]], evidence_id: str) -> str | None:
    for event in events:
        if str(event.get("id")) != evidence_id:
            continue
        command = str(event.get("command") or "").strip()
        if command:
            return command
    return None


def require_command_identity(events: list[dict[str, object]], evidence_id: str, command: str) -> None:
    """Reject reusing an evidence ID for a different verification command."""
    known = _known_command(events, evidence_id)
    if known is None:
        return
    if _canonical_command(known) != _canonical_command(command):
        raise ValueError(
            f"evidence id {evidence_id} is already bound to `{known}`; refusing different command `{command}`"
        )


def current_states(
    events: list[dict[str, object]], current_snapshot: RepoSnapshot | None = None
) -> list[EvidenceState]:
    states: dict[str, EvidenceState] = {}
    bound_commands: dict[str, str] = {}
    order: list[str] = []
    for event in events:
        event_id = str(event["id"])
        if event_id not in states:
            order.append(event_id)
        previous = states.get(event_id)
        label = str(event.get("label") or (previous.label if previous else event_id))
        command = str(event.get("command") or (previous.command if previous else ""))
        if command:
            known = bound_commands.get(event_id)
            if known is not None and _canonical_command(known) != _canonical_command(command):
                raise ValueError(f"ledger command identity changed for evidence id {event_id}")
            bound_commands[event_id] = known or command

        kind = str(event["event"])
        timestamp = str(event.get("timestamp", ""))
        if kind == "plan":
            states[event_id] = EvidenceState(event_id, label, command, "planned", timestamp)
            continue
        if kind not in {"run", "record"}:
            raise ValueError(f"unsupported ledger event type: {kind}")

        exit_code = int(event["exit_code"])
        duration = event.get("duration_seconds")
        source = "executed" if kind == "run" else "external"
        changed = bool(event.get("state_changed_during_run", False))
        allowed_change = bool(event.get("allow_state_change", False))
        snapshot = _event_snapshot(event)

        status = "failed"
        if exit_code == 0:
            if source == "external":
                status = "external"
            elif changed and not allowed_change:
                status = "mutated"
            elif not snapshot.repo_root or not snapshot.state_fingerprint:
                status = "unbound"
            elif _snapshot_is_stale(snapshot, current_snapshot):
                status = "stale"
            else:
                status = "verified"
        states[event_id] = EvidenceState(
            id=event_id,
            label=label,
            command=command,
            status=status,
            timestamp=timestamp,
            exit_code=exit_code,
            duration_seconds=float(duration) if duration is not None else None,
            source=source,
            cwd=str(event["cwd"]) if event.get("cwd") else None,
            repo_root=snapshot.repo_root,
            git_head=snapshot.git_head,
            state_fingerprint=snapshot.state_fingerprint,
            state_changed_during_run=changed,
            allow_state_change=allowed_change,
        )
    return [states[event_id] for event_id in order]


def render_report(states: list[EvidenceState], pending_tests: list[object] | None = None) -> str:
    verified = [state for state in states if state.status == "verified"]
    not_verified = [state for state in states if state.status != "verified"]
    lines = ["## Verified"]
    if verified:
        for state in verified:
            lines.append(f"- {state.label}: `{state.command}` — exit 0 at {state.timestamp}")
    else:
        lines.append("- None recorded.")

    lines.extend(["", "## Not verified"])
    if not_verified:
        for state in not_verified:
            if state.status == "planned":
                reason = "planned but not run"
            elif state.status == "failed":
                reason = f"failed with exit {state.exit_code}"
            elif state.status == "stale":
                reason = "previously passed, but repository state changed afterward; rerun required"
            elif state.status == "external":
                reason = "externally recorded exit 0; not executed by this ledger"
            elif state.status == "unbound":
                reason = "exit 0 but evidence is not bound to a Git repository state"
            elif state.status == "mutated":
                reason = "verification command changed repository state; rerun on the resulting candidate"
            else:
                reason = state.status
            lines.append(f"- {state.label}: `{state.command}` — {reason} at {state.timestamp}")

    pending_tests = pending_tests or []
    for item in pending_tests:
        item_id = getattr(item, "id", "pending")
        command = getattr(item, "command", "")
        trigger = getattr(item, "trigger", "unspecified trigger")
        lines.append(f"- Pending test {item_id}: `{command}` — still required ({trigger})")

    if not not_verified and not pending_tests:
        lines.append("- None.")
    return "\n".join(lines)


def evidence_state_by_id(
    ledger: Path, evidence_id: str, repo: Path | None = None
) -> EvidenceState | None:
    snapshot = repository_snapshot(repo) if repo is not None else repository_snapshot()
    for state in current_states(load_events(ledger), snapshot):
        if state.id == evidence_id:
            return state
    return None


def new_id() -> str:
    return f"EV-{uuid.uuid4().hex[:8]}"


def _snapshot_fields(snapshot: RepoSnapshot) -> dict[str, str | None]:
    return {
        "repo_root": snapshot.repo_root,
        "git_head": snapshot.git_head,
        "state_fingerprint": snapshot.state_fingerprint,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record verification evidence and render Verified / Not verified sections.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help=f"Ledger path (default: {DEFAULT_LEDGER})")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository used for staleness checks (default: current directory)")
    subparsers = parser.add_subparsers(dest="action", required=True)

    plan_parser = subparsers.add_parser("plan", help="Register a command that should be verified")
    plan_parser.add_argument("--id", default=None)
    plan_parser.add_argument("--label", required=True)
    plan_parser.add_argument("--command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a command and record its exit code plus repository state")
    run_parser.add_argument("--id", default=None)
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument("--cwd", type=Path, default=None, help="Working directory for the command")
    run_parser.add_argument(
        "--allow-state-change",
        action="store_true",
        help="Allow this verification command to modify repository state; use only for deliberate generators/formatters",
    )
    run_parser.add_argument("command", nargs=argparse.REMAINDER)

    record_parser = subparsers.add_parser("record", help="Record evidence produced by another runner; it is not treated as locally verified")
    record_parser.add_argument("--id", default=None)
    record_parser.add_argument("--label", required=True)
    record_parser.add_argument("--command", required=True)
    record_parser.add_argument("--exit-code", required=True, type=int)

    report_parser = subparsers.add_parser("report", help="Render Verified / Not verified sections")
    report_parser.add_argument("--pending-tests", type=Path, default=Path("PENDING_TESTS.md"), help="Include outstanding PENDING_TESTS.md entries when the file exists")
    args = parser.parse_args(argv)

    try:
        events = load_events(args.ledger)
        if args.action == "plan":
            event_id = args.id or new_id()
            require_command_identity(events, event_id, args.command)
            append_event(args.ledger, {
                "event": "plan",
                "id": event_id,
                "label": args.label,
                "command": args.command,
                "timestamp": utc_now(),
            })
            print(event_id)
            return 0

        if args.action == "run":
            command = args.command[1:] if args.command and args.command[0] == "--" else args.command
            if not command:
                raise ValueError("run command must not be empty")
            event_id = args.id or new_id()
            command_text = shlex.join(command)
            require_command_identity(events, event_id, command_text)
            command_cwd = (args.cwd or args.repo).resolve()
            before = repository_snapshot(args.repo)
            started = time.monotonic()
            completed = subprocess.run(command, cwd=str(command_cwd), check=False)
            duration = time.monotonic() - started
            after = repository_snapshot(args.repo)
            changed = before != after
            append_event(args.ledger, {
                "event": "run",
                "id": event_id,
                "label": args.label,
                "command": command_text,
                "cwd": str(command_cwd),
                "exit_code": completed.returncode,
                "duration_seconds": round(duration, 6),
                "timestamp": utc_now(),
                **_snapshot_fields(after),
                "state_changed_during_run": changed,
                "allow_state_change": bool(args.allow_state_change),
            })
            return completed.returncode

        if args.action == "record":
            event_id = args.id or new_id()
            require_command_identity(events, event_id, args.command)
            snapshot = repository_snapshot(args.repo)
            append_event(args.ledger, {
                "event": "record",
                "id": event_id,
                "label": args.label,
                "command": args.command,
                "exit_code": args.exit_code,
                "timestamp": utc_now(),
                "source": "external",
                **_snapshot_fields(snapshot),
            })
            print(event_id)
            return 0

        snapshot = repository_snapshot(args.repo)
        states = current_states(events, snapshot)
        pending: list[object] = []
        if args.pending_tests.exists():
            try:
                from scripts.pending_tests import load_items
            except ModuleNotFoundError:
                from pending_tests import load_items
            pending = list(load_items(args.pending_tests))
        print(render_report(states, pending))
        return 0
    except (ValueError, OSError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
