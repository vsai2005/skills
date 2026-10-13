#!/usr/bin/env python3
"""Canonicalize and lock verification commands to Evidence IDs."""

from __future__ import annotations

import re
import shlex


def canonical_command(command: str) -> tuple[str, ...]:
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


def require_command_identity(
    events: list[dict[str, object]], evidence_id: str, command: str
) -> None:
    """Reject reusing an Evidence ID for a different verification command."""
    known = _known_command(events, evidence_id)
    if known is None:
        return
    if canonical_command(known) != canonical_command(command):
        raise ValueError(
            f"evidence id {evidence_id} is already bound to `{known}`; "
            f"refusing different command `{command}`"
        )
