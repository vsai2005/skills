#!/usr/bin/env python3
"""Deterministic integrity and style grader for voice-aware humanizer eval."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.humanizer_audit import audit_text, compare_texts
from scripts.voice_profile import compare_profiles, profile_text

REQUIRED = (
    "Queue Worker",
    "v3.1",
    "us-east-2",
    "12%",
    "8 seconds",
    "no database migration",
    "250 items",
    "November 6",
)


def grade_workspace(workspace: Path) -> list[str]:
    target = workspace / "HUMANIZED.md"
    draft = workspace / "DRAFT.md"
    sample = workspace / "VOICE_SAMPLE.md"
    if not target.is_file():
        return ["HUMANIZED.md is missing"]
    text = target.read_text(encoding="utf-8")
    low = text.lower()
    problems: list[str] = []
    for fact in REQUIRED:
        if fact.lower() not in low:
            problems.append(f"missing required fact: {fact}")

    integrity = compare_texts(draft.read_text(encoding="utf-8"), text)
    if integrity["missing_literals"]:
        problems.append(f"missing protected literals: {integrity['missing_literals']}")
    if integrity["missing_modals"] or integrity["missing_negations"]:
        problems.append("modal or negation preservation changed")

    audit = audit_text(text)
    high_or_medium = [x for x in audit["signals"] if x["severity"] in {"high", "medium"}]
    if high_or_medium:
        problems.append("naturalness audit still has high/medium signals")

    reference = profile_text(sample.read_text(encoding="utf-8"))
    candidate = profile_text(text)
    comparison = compare_profiles(reference, candidate)
    severe_style_drift = {
        "sentence_words_mean",
        "explicit_transitions_per_100_words",
        "long_word_ratio",
    }.intersection(comparison["large_differences"])
    if len(severe_style_drift) >= 2:
        problems.append(f"candidate diverges strongly from voice sample: {sorted(severe_style_drift)}")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    if len(args) != 1:
        print("usage: grade_humanizer_voice.py WORKSPACE", file=sys.stderr)
        return 2
    problems = grade_workspace(Path(args[0]))
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print("voice-aware rewrite preserves facts and avoids formulaic drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
