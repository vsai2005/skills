#!/usr/bin/env python3
"""Maintain a small, script-managed PENDING_TESTS.md queue."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

MARKER_RE = re.compile(r"^<!-- pending-test: (\{.*\}) -->$", re.MULTILINE)
HEADER = (
    "# Pending Tests\n\n"
    "Managed by `scripts/pending_tests.py`. Each item must have a reason and an explicit trigger for running it. "
    "Completion requires current executed evidence or an explicit superseding reason.\n\n"
)


@dataclass(frozen=True)
class PendingTest:
    id: str
    command: str
    reason: str
    trigger: str
    created_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_items(path: Path) -> list[PendingTest]:
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc

    items: list[PendingTest] = []
    seen: set[str] = set()
    for match in MARKER_RE.finditer(text):
        try:
            data = json.loads(match.group(1))
            item = PendingTest(
                id=str(data["id"]),
                command=str(data["command"]),
                reason=str(data["reason"]),
                trigger=str(data["trigger"]),
                created_at=str(data["created_at"]),
            )
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid pending-test marker in {path}: {exc}") from exc
        if not all((item.id.strip(), item.command.strip(), item.reason.strip(), item.trigger.strip(), item.created_at.strip())):
            raise ValueError(f"pending test contains an empty required field in {path}")
        if item.id in seen:
            raise ValueError(f"duplicate pending test id {item.id!r} in {path}")
        seen.add(item.id)
        items.append(item)
    return items


def render(items: list[PendingTest]) -> str:
    lines = [HEADER.rstrip(), ""]
    if not items:
        lines.append("No pending tests.\n")
        return "\n".join(lines)
    for item in items:
        payload = json.dumps(asdict(item), sort_keys=True, separators=(",", ":"))
        lines.extend([
            f"<!-- pending-test: {payload} -->",
            f"- [ ] **{item.id}** — `{item.command}`",
            f"  - Reason: {item.reason}",
            f"  - Trigger: {item.trigger}",
            f"  - Added: {item.created_at}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_items(path: Path, items: list[PendingTest]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(items), encoding="utf-8", newline="\n")


def add_item(path: Path, command: str, reason: str, trigger: str) -> PendingTest:
    if not command.strip() or not reason.strip() or not trigger.strip():
        raise ValueError("command, reason, and trigger must all be non-empty")
    items = load_items(path)
    item = PendingTest(
        id=f"PT-{uuid.uuid4().hex[:8]}",
        command=command.strip(),
        reason=reason.strip(),
        trigger=trigger.strip(),
        created_at=utc_now(),
    )
    write_items(path, [*items, item])
    return item


def _commands_equivalent(left: str, right: str) -> bool:
    try:
        return shlex.split(left) == shlex.split(right)
    except ValueError:
        return " ".join(left.split()) == " ".join(right.split())


def _require_completion_evidence(
    item: PendingTest,
    evidence_id: str | None,
    superseded_by: str | None,
    ledger: Path,
    repo: Path,
) -> None:
    if bool(evidence_id) == bool(superseded_by):
        raise ValueError("complete requires exactly one of --evidence-id or --superseded-by")
    if superseded_by:
        if len(superseded_by.strip()) < 8:
            raise ValueError("--superseded-by must explain the equivalent replacement check")
        return

    try:
        from scripts.evidence_ledger import evidence_state_by_id
    except ModuleNotFoundError:
        from evidence_ledger import evidence_state_by_id
    state = evidence_state_by_id(ledger, str(evidence_id), repo)
    if state is None:
        raise ValueError(f"evidence id not found: {evidence_id}")
    if state.status != "verified":
        raise ValueError(f"evidence {evidence_id} is not current verified evidence (status: {state.status})")
    if not _commands_equivalent(state.command, item.command):
        raise ValueError(
            f"evidence {evidence_id} ran a different command; use matching evidence or explicit --superseded-by"
        )


def _append_history(
    history: Path,
    item: PendingTest,
    *,
    evidence_id: str | None,
    superseded_by: str | None,
) -> None:
    history.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event": "completed",
        "completed_at": utc_now(),
        "pending_test": asdict(item),
        "evidence_id": evidence_id,
        "superseded_by": superseded_by,
    }
    with history.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def complete_item(
    path: Path,
    item_id: str,
    *,
    evidence_id: str | None = None,
    superseded_by: str | None = None,
    ledger: Path = Path(".verification/evidence.jsonl"),
    repo: Path = Path("."),
    history: Path | None = None,
) -> PendingTest:
    items = load_items(path)
    found = next((item for item in items if item.id == item_id), None)
    if found is None:
        raise ValueError(f"pending test id not found: {item_id}")
    _require_completion_evidence(found, evidence_id, superseded_by, ledger, repo)
    write_items(path, [candidate for candidate in items if candidate.id != item_id])
    if history is not None:
        _append_history(
            history,
            found,
            evidence_id=evidence_id,
            superseded_by=superseded_by,
        )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Maintain PENDING_TESTS.md for deferred heavy verification.")
    parser.add_argument("--file", type=Path, default=Path("PENDING_TESTS.md"), help="Pending test file (default: PENDING_TESTS.md)")
    parser.add_argument("--ledger", type=Path, default=Path(".verification/evidence.jsonl"), help="Evidence ledger used to complete items")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository used to validate evidence freshness")
    parser.add_argument(
        "--history",
        type=Path,
        default=Path(".verification/pending_tests_history.jsonl"),
        help="Append completed/superseded item history here",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    add_parser = subparsers.add_parser("add", help="Add a pending test")
    add_parser.add_argument("--command", required=True)
    add_parser.add_argument("--reason", required=True)
    add_parser.add_argument("--trigger", required=True)

    done_parser = subparsers.add_parser("complete", help="Remove a completed/superseded pending test")
    done_parser.add_argument("id")
    done_parser.add_argument("--evidence-id", default=None, help="Current verified evidence ID proving the check ran")
    done_parser.add_argument("--superseded-by", default=None, help="Explain the equivalent check that replaced this item")

    subparsers.add_parser("list", help="List pending tests")
    subparsers.add_parser("check", help="Exit 1 when pending tests remain")
    subparsers.add_parser("init", help="Create an empty managed file when missing")
    args = parser.parse_args(argv)

    try:
        if args.action == "add":
            item = add_item(args.file, args.command, args.reason, args.trigger)
            print(f"[OK] Added {item.id}")
            return 0
        if args.action == "complete":
            item = complete_item(
                args.file,
                args.id,
                evidence_id=args.evidence_id,
                superseded_by=args.superseded_by,
                ledger=args.ledger,
                repo=args.repo,
                history=args.history,
            )
            print(f"[OK] Completed {item.id}")
            return 0
        if args.action == "init":
            if not args.file.exists():
                write_items(args.file, [])
            print(f"[OK] {args.file}")
            return 0

        items = load_items(args.file)
        if args.action == "list":
            if not items:
                print("No pending tests.")
            else:
                for item in items:
                    print(f"{item.id}\t{item.command}\t{item.trigger}\t{item.reason}")
            return 0
        if args.action == "check":
            if items:
                print(f"[PENDING] {len(items)} deferred test(s) remain")
                return 1
            print("[OK] No pending tests")
            return 0
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
