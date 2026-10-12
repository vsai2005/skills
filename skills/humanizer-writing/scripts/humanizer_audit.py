#!/usr/bin/env python3
"""Audit prose naturalness and compare rewrites for deterministic integrity risks.

This helper reports writing signals. It does not decide authorship and it does not
attempt to predict or bypass AI-detection systems.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

GENERIC_OPENERS = (
    "in today's fast-paced",
    "in today's rapidly evolving",
    "in the ever-evolving",
    "in the modern world",
    "it is important to note",
    "it is worth noting",
    "when it comes to",
)
TRANSITIONS = (
    "furthermore",
    "moreover",
    "additionally",
    "in conclusion",
    "overall",
    "ultimately",
    "notably",
)
EMPTY_PRAISE = (
    "robust",
    "seamless",
    "powerful",
    "comprehensive",
    "game-changing",
    "cutting-edge",
    "innovative",
    "transformative",
    "significant improvement",
)
MODALS = ("may", "might", "can", "could", "should", "must", "will", "would")
NEGATIONS = ("no", "not", "never", "without", "unchanged", "cannot", "can't", "won't", "mustn't", "shouldn't")

TOKEN_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
URL_RE = re.compile(r"https?://[^\s)\]>]+")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
QUOTED_RE = re.compile(r"(?:(?<=\s)|^)([\"“][^\"”\n]{1,120}[\"”])")
VERSION_OR_NUMBER_RE = re.compile(r"(?<!\w)(?:v?\d+(?:[.,]\d+)*(?:%|[A-Za-z]+)?)(?!\w)")
CODELIKE_RE = re.compile(r"\b(?=[A-Z0-9_-]*\d)[A-Z][A-Z0-9_-]{2,}\b")


def words(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def sentences(text: str) -> list[str]:
    clean = re.sub(r"[`*_#]", "", text)
    return [part.strip() for part in SENTENCE_SPLIT_RE.split(clean) if part.strip()]


def paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def _severity_count(count: int, medium: int, high: int) -> str | None:
    if count >= high:
        return "high"
    if count >= medium:
        return "medium"
    if count > 0:
        return "low"
    return None


def _signal(code: str, severity: str, message: str, count: int | None = None) -> dict:
    out = {"code": code, "severity": severity, "message": message}
    if count is not None:
        out["count"] = count
    return out


def audit_text(text: str) -> dict:
    low = text.lower()
    sents = sentences(text)
    paras = paragraphs(text)
    signals: list[dict] = []

    opener_hits = [phrase for phrase in GENERIC_OPENERS if phrase in low]
    if opener_hits:
        signals.append(_signal("generic_opener", "high", f"generic opener detected: {opener_hits[0]}", len(opener_hits)))

    transition_count = sum(len(re.findall(rf"\b{re.escape(item)}\b", low)) for item in TRANSITIONS)
    sev = _severity_count(transition_count, 2, 4)
    if sev:
        signals.append(_signal("formulaic_transitions", sev, "repeated formulaic transition language", transition_count))

    praise_count = sum(len(re.findall(rf"\b{re.escape(item)}\b", low)) for item in EMPTY_PRAISE)
    sev = _severity_count(praise_count, 2, 4)
    if sev:
        signals.append(_signal("empty_praise", sev, "generic praise or marketing language", praise_count))

    openings: list[str] = []
    for sent in sents:
        toks = [token.lower() for token in words(sent)]
        if toks:
            openings.append(" ".join(toks[:2]))
    if openings:
        repeated_opening, repeated_count = Counter(openings).most_common(1)[0]
        if repeated_count >= 3:
            severity = "high" if repeated_count >= 5 else "medium"
            signals.append(_signal("repeated_sentence_openings", severity, f"sentence openings repeat: {repeated_opening!r}", repeated_count))

    lengths = [len(words(sent)) for sent in sents]
    mean_len = statistics.fmean(lengths) if lengths else 0.0
    stdev_len = statistics.pstdev(lengths) if len(lengths) >= 2 else 0.0
    cv = (stdev_len / mean_len) if mean_len else 0.0
    if len(lengths) >= 5 and cv < 0.15:
        signals.append(_signal("uniform_sentence_rhythm", "medium", "sentence lengths are unusually uniform"))

    para_lengths = [len(words(para)) for para in paras]
    if len(para_lengths) >= 3:
        pmean = statistics.fmean(para_lengths)
        pcv = statistics.pstdev(para_lengths) / pmean if pmean else 0.0
        if pcv < 0.15:
            signals.append(_signal("uniform_paragraph_shape", "low", "paragraph sizes are unusually uniform"))
    else:
        pcv = 0.0

    word_count = len(words(text))
    long_words = [w for w in words(text) if len(w) >= 12 and w.isalpha()]
    long_word_ratio = (len(long_words) / word_count) if word_count else 0.0
    if word_count >= 80 and long_word_ratio > 0.12:
        signals.append(_signal("dense_wording", "low", "high share of long words may make the prose feel over-engineered", len(long_words)))

    high = sum(1 for item in signals if item["severity"] == "high")
    medium = sum(1 for item in signals if item["severity"] == "medium")
    return {
        "word_count": word_count,
        "sentence_count": len(sents),
        "paragraph_count": len(paras),
        "mean_sentence_words": round(mean_len, 2),
        "sentence_length_cv": round(cv, 3),
        "paragraph_length_cv": round(pcv, 3),
        "long_word_ratio": round(long_word_ratio, 3),
        "signals": signals,
        "already_good": high == 0 and medium == 0,
    }


def protected_literals(text: str) -> list[str]:
    found: set[str] = set()
    for regex in (URL_RE, INLINE_CODE_RE, VERSION_OR_NUMBER_RE, CODELIKE_RE):
        found.update(match.group(0) for match in regex.finditer(text))
    found.update(match.group(1) for match in QUOTED_RE.finditer(text))
    return sorted(found, key=lambda item: (item.lower(), item))


def _word_occurrences(text: str, terms: tuple[str, ...]) -> Counter:
    low_words = [w.lower() for w in words(text)]
    counts = Counter(low_words)
    return Counter({term: counts[term] for term in terms if counts[term]})


def compare_texts(source: str, rewrite: str) -> dict:
    source_literals = protected_literals(source)
    rewrite_literals = set(protected_literals(rewrite))
    missing_literals = [item for item in source_literals if item not in rewrite_literals and item not in rewrite]

    source_modals = _word_occurrences(source, MODALS)
    rewrite_modals = _word_occurrences(rewrite, MODALS)
    missing_modals = {
        term: count - rewrite_modals.get(term, 0)
        for term, count in source_modals.items()
        if rewrite_modals.get(term, 0) < count
    }

    source_neg = _word_occurrences(source, NEGATIONS)
    rewrite_neg = _word_occurrences(rewrite, NEGATIONS)
    missing_negations = {
        term: count - rewrite_neg.get(term, 0)
        for term, count in source_neg.items()
        if rewrite_neg.get(term, 0) < count
    }

    src_words = max(1, len(words(source)))
    rewrite_words = len(words(rewrite))
    length_ratio = rewrite_words / src_words
    warnings: list[str] = []
    if missing_literals:
        warnings.append("protected literals from the source are missing")
    if missing_modals:
        warnings.append("source uncertainty/obligation modal language may have changed")
    if missing_negations:
        warnings.append("source negation language may have changed")
    if length_ratio < 0.55:
        warnings.append("rewrite is much shorter than the source; omission risk is high")
    elif length_ratio > 1.8:
        warnings.append("rewrite is much longer than the source; invention or padding risk is high")

    return {
        "source_word_count": src_words,
        "rewrite_word_count": rewrite_words,
        "length_ratio": round(length_ratio, 3),
        "protected_literals": source_literals,
        "missing_literals": missing_literals,
        "missing_modals": missing_modals,
        "missing_negations": missing_negations,
        "warnings": warnings,
        "integrity_ok": not warnings,
    }


def _print_audit(result: dict) -> None:
    print("Humanizer Audit")
    print("===============")
    print(f"Words: {result['word_count']}")
    print(f"Sentences: {result['sentence_count']}")
    print(f"Paragraphs: {result['paragraph_count']}")
    print(f"Sentence-length variation (CV): {result['sentence_length_cv']}")
    if result["signals"]:
        print("Signals:")
        for item in result["signals"]:
            suffix = f" ({item['count']})" if "count" in item else ""
            print(f"- {item['severity'].upper()}: {item['message']}{suffix}")
    else:
        print("Signals: none")
    print(f"Already-good stop condition: {'yes' if result['already_good'] else 'no'}")


def _print_compare(result: dict) -> None:
    print("Humanizer Integrity Check")
    print("========================")
    print(f"Length ratio: {result['length_ratio']}")
    print(f"Protected literals checked: {len(result['protected_literals'])}")
    if result["missing_literals"]:
        print("Missing literals:")
        for item in result["missing_literals"]:
            print(f"- {item}")
    if result["missing_modals"]:
        print(f"Missing modal language: {dict(result['missing_modals'])}")
    if result["missing_negations"]:
        print(f"Missing negation language: {dict(result['missing_negations'])}")
    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"- {warning}")
    else:
        print("Warnings: none")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit prose naturalness or compare a rewrite with its source.")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Report naturalness signals in one text file.")
    audit.add_argument("path", type=Path)
    audit.add_argument("--json", action="store_true")
    audit.add_argument("--fail-on-high", action="store_true")

    compare = sub.add_parser("compare", help="Check a rewrite for deterministic preservation risks.")
    compare.add_argument("source", type=Path)
    compare.add_argument("rewrite", type=Path)
    compare.add_argument("--json", action="store_true")
    compare.add_argument("--fail-on-warning", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            result = audit_text(args.path.read_text(encoding="utf-8"))
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                _print_audit(result)
            has_high = any(item["severity"] == "high" for item in result["signals"])
            return 1 if args.fail_on_high and has_high else 0

        result = compare_texts(
            args.source.read_text(encoding="utf-8"),
            args.rewrite.read_text(encoding="utf-8"),
        )
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            _print_compare(result)
        return 1 if args.fail_on_warning and result["warnings"] else 0
    except (OSError, UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
