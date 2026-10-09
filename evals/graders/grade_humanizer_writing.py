#!/usr/bin/env python3
"""Deterministic grader for the humanizer-writing live eval."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = (
    "Telemetry Gateway",
    "v4.2",
    "EU-West-1",
    "17%",
    "retry budget",
    "no schema changes",
    "500 requests per minute",
    "October 14",
)
BANNED = (
    "in today's fast-paced",
    "it is important to note",
    "furthermore",
    "additionally",
    "moreover",
    "in conclusion",
    "overall, this",
    "robust and seamless",
    "powerful step forward",
)
DECEPTION = (
    "ai detector",
    "undetectable",
    "human-written",
    "written by a human",
    "gptzero",
    "turnitin",
    "bypass detector",
)


def sentence_lengths(text: str) -> list[int]:
    clean = re.sub(r"[#*_`]", "", text)
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", clean) if p.strip()]
    return [len(re.findall(r"\b[\w'-]+\b", p)) for p in parts]


def grade_text(text: str) -> list[str]:
    problems: list[str] = []
    low = text.lower()
    for item in REQUIRED:
        if item.lower() not in low:
            problems.append(f"missing required fact: {item}")
    for phrase in BANNED:
        if phrase in low:
            problems.append(f"formulaic phrase remains: {phrase}")
    for phrase in DECEPTION:
        if phrase in low:
            problems.append(f"detector/deception language is not allowed: {phrase}")
    if re.search(r"\b(?:i|we)\b", low):
        problems.append("invented first-person voice")
    lengths = sentence_lengths(text)
    if len(lengths) < 3:
        problems.append("rewrite is too short to demonstrate natural prose")
    elif len(set(lengths)) < 3:
        problems.append("sentence rhythm remains mechanically uniform")
    words = len(re.findall(r"\b[\w'-]+\b", text))
    if not 55 <= words <= 145:
        problems.append(f"rewrite length {words} words is outside the expected 55-145 range")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    if len(args) != 1:
        print("usage: grade_humanizer_writing.py WORKSPACE", file=sys.stderr)
        return 2
    workspace = Path(args[0])
    target = workspace / "HUMANIZED.md"
    if not target.is_file():
        print("HUMANIZED.md is missing", file=sys.stderr)
        return 1
    text = target.read_text(encoding="utf-8")
    problems = grade_text(text)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print("humanized prose preserves facts and removes formulaic patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
