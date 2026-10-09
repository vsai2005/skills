#!/usr/bin/env python3
"""Deterministic grader for the ASD-STE100-inspired writing live eval."""
from __future__ import annotations

import re
import sys
from pathlib import Path

BAD_PHRASES = (
    "due to the fact that",
    "in order to",
    "utilize",
    "whether or not",
    "make a determination",
    "perform a restart",
)
REQUIRED = ("Data Service", "Restart Service", "30 seconds", "Status", "READY", "E104", "database configuration", "support team")


def sentences(text: str) -> list[str]:
    cleaned = re.sub(r"`[^`]+`", "IDENT", text)
    return [s.strip(" \n-*#\t") for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]


def word_count(sentence: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", sentence))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: grade_asd_ste100_writing.py WORKSPACE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]) / "REVISED.md"
    if not path.is_file():
        print("REVISED.md missing")
        return 1
    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    missing = [item for item in REQUIRED if item not in text]
    bad = [phrase for phrase in BAD_PHRASES if phrase in lower]
    long_sentences = [s for s in sentences(text) if word_count(s) > 30]
    direct_action = bool(re.search(r"(?mi)^\s*(?:\d+[.)]\s*)?(?:if\b[^\n]*,\s*)?(?:select|restart|wait|check|verify|contact|do not)\b", text))

    problems: list[str] = []
    if missing:
        problems.append("missing required technical details: " + ", ".join(missing))
    if bad:
        problems.append("wordy phrases remain: " + ", ".join(bad))
    if long_sentences:
        problems.append(f"{len(long_sentences)} sentence(s) exceed 30 words")
    if not direct_action:
        problems.append("no clear direct procedural action found")

    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("ASD-STE100-inspired rewrite preserved required facts and improved controlled-English signals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
