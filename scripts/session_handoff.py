#!/usr/bin/env python3
"""Create a compact, auditable handoff for a long-running coding task."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _git(root: Path, args: list[str]) -> str | None:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def _changed(root: Path) -> list[str]:
    proc = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1"], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    result=[]
    for line in proc.stdout.splitlines():
        if len(line)>=4:
            result.append(line[3:].split(" -> ")[-1])
    return sorted(set(result))


def _pending(root: Path) -> list[str]:
    path = root / "PENDING_TESTS.md"
    if not path.is_file(): return []
    items=[]
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("- [ ] "): items.append(line[6:].strip())
    return items


def make_handoff(
    root: Path, *, goal: str, scope: list[str], decisions: list[str], remaining: list[str],
    failures: list[str], evidence: list[str], docs: list[str], notes: list[str],
) -> dict[str, Any]:
    root=root.resolve()
    if not root.is_dir(): raise ValueError(f"repository root is not a directory: {root}")
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "accepted_scope": scope,
        "git_head": _git(root, ["rev-parse", "HEAD"]),
        "branch": _git(root, ["branch", "--show-current"]),
        "changed_files": _changed(root),
        "important_decisions": decisions,
        "remaining_work": remaining,
        "known_failures": failures,
        "verification_evidence_ids": evidence,
        "pending_tests": _pending(root),
        "relevant_docs": docs,
        "notes": notes,
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines=["# Session Handoff", "", f"Created: {data['created_utc']}", f"Git HEAD: {data['git_head'] or 'unbound'}", f"Branch: {data['branch'] or '(unknown)'}", "", "## Goal", "", data['goal']]
    for title,key in [("Accepted scope","accepted_scope"),("Changed files","changed_files"),("Important decisions","important_decisions"),("Remaining work","remaining_work"),("Known failures","known_failures"),("Verification evidence IDs","verification_evidence_ids"),("Pending tests","pending_tests"),("Relevant docs","relevant_docs"),("Notes","notes")]:
        lines += ["", f"## {title}", ""]
        values=data.get(key,[])
        lines += [f"- {v}" for v in values] if values else ["- None"]
    return "\n".join(lines)+"\n"


def main(argv: list[str] | None=None)->int:
    p=argparse.ArgumentParser(description="Create a compact session-handoff record.")
    p.add_argument("root", nargs="?", default=".", type=Path)
    p.add_argument("--goal", required=True)
    p.add_argument("--scope", action="append", default=[])
    p.add_argument("--decision", action="append", default=[])
    p.add_argument("--remaining", action="append", default=[])
    p.add_argument("--failure", action="append", default=[])
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--doc", action="append", default=[])
    p.add_argument("--note", action="append", default=[])
    p.add_argument("--output", type=Path, default=Path("HANDOFF.md"))
    p.add_argument("--json", action="store_true")
    a=p.parse_args(argv)
    try:
        data=make_handoff(a.root, goal=a.goal, scope=a.scope, decisions=a.decision, remaining=a.remaining, failures=a.failure, evidence=a.evidence, docs=a.doc, notes=a.note)
    except (ValueError,OSError,UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr); return 2
    text=json.dumps(data,indent=2,sort_keys=True)+"\n" if a.json else render_markdown(data)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text,encoding="utf-8",newline="\n")
    print(f"[OK] Wrote {a.output}")
    return 0

if __name__=="__main__":
    sys.exit(main())
