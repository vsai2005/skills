#!/usr/bin/env python3
"""Create a compact style profile from an authentic writing sample.

The profile describes observable writing tendencies. It must not be used to infer
identity, demographics, or hidden personal traits.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
CONTRACTION_RE = re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'d|'m|'s)\b", re.IGNORECASE)
FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|mine|we|us|our|ours)\b", re.IGNORECASE)
SECOND_PERSON_RE = re.compile(r"\b(?:you|your|yours)\b", re.IGNORECASE)
TRANSITION_RE = re.compile(r"(?im)^\s*(?:however|furthermore|moreover|additionally|therefore|thus|overall|in conclusion)[, ]")


def _words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def _sentences(text: str) -> list[str]:
    clean = re.sub(r"[`*_#]", "", text)
    return [x.strip() for x in SENTENCE_RE.split(clean) if x.strip()]


def _paragraphs(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"\n\s*\n", text) if x.strip()]


def _per_100(count: int, words: int) -> float:
    return round((count * 100.0 / words), 2) if words else 0.0


def profile_text(text: str) -> dict:
    words = _words(text)
    sents = _sentences(text)
    paras = _paragraphs(text)
    sentence_lengths = [len(_words(s)) for s in sents]
    paragraph_lengths = [len(_words(p)) for p in paras]
    word_count = len(words)
    alpha_words = [w for w in words if w.isalpha()]
    long_word_count = sum(1 for w in alpha_words if len(w) >= 10)

    result = {
        "word_count": word_count,
        "sentence_count": len(sents),
        "paragraph_count": len(paras),
        "sentence_words_mean": round(statistics.fmean(sentence_lengths), 2) if sentence_lengths else 0.0,
        "sentence_words_median": round(statistics.median(sentence_lengths), 2) if sentence_lengths else 0.0,
        "sentence_words_stdev": round(statistics.pstdev(sentence_lengths), 2) if len(sentence_lengths) >= 2 else 0.0,
        "short_sentence_ratio": round(sum(1 for x in sentence_lengths if x <= 8) / len(sentence_lengths), 3) if sentence_lengths else 0.0,
        "long_sentence_ratio": round(sum(1 for x in sentence_lengths if x >= 24) / len(sentence_lengths), 3) if sentence_lengths else 0.0,
        "paragraph_words_mean": round(statistics.fmean(paragraph_lengths), 2) if paragraph_lengths else 0.0,
        "contractions_per_100_words": _per_100(len(CONTRACTION_RE.findall(text)), word_count),
        "first_person_per_100_words": _per_100(len(FIRST_PERSON_RE.findall(text)), word_count),
        "second_person_per_100_words": _per_100(len(SECOND_PERSON_RE.findall(text)), word_count),
        "questions_per_100_words": _per_100(text.count("?"), word_count),
        "exclamations_per_100_words": _per_100(text.count("!"), word_count),
        "semicolons_per_100_words": _per_100(text.count(";"), word_count),
        "em_dashes_per_100_words": _per_100(text.count("—"), word_count),
        "explicit_transitions_per_100_words": _per_100(len(TRANSITION_RE.findall(text)), word_count),
        "long_word_ratio": round(long_word_count / len(alpha_words), 3) if alpha_words else 0.0,
    }
    return result


def compare_profiles(reference: dict, candidate: dict) -> dict:
    keys = (
        "sentence_words_mean",
        "sentence_words_stdev",
        "short_sentence_ratio",
        "long_sentence_ratio",
        "paragraph_words_mean",
        "contractions_per_100_words",
        "first_person_per_100_words",
        "second_person_per_100_words",
        "questions_per_100_words",
        "semicolons_per_100_words",
        "em_dashes_per_100_words",
        "explicit_transitions_per_100_words",
        "long_word_ratio",
    )
    deltas = {key: round(float(candidate[key]) - float(reference[key]), 3) for key in keys}
    large: list[str] = []
    relative_keys = {"sentence_words_mean", "sentence_words_stdev", "paragraph_words_mean"}
    for key, delta in deltas.items():
        base = abs(float(reference[key]))
        if key in relative_keys:
            threshold = max(4.0, base * 0.45)
        else:
            threshold = max(0.15, base * 1.5)
        if abs(delta) > threshold:
            large.append(key)
    return {"deltas": deltas, "large_differences": sorted(large), "close_enough": not large}


def _print_profile(profile: dict) -> None:
    print("Voice Profile")
    print("=============")
    print(f"Words: {profile['word_count']}")
    print(f"Sentence length: mean {profile['sentence_words_mean']}, stdev {profile['sentence_words_stdev']}")
    print(f"Paragraph length mean: {profile['paragraph_words_mean']}")
    print(f"Contractions/100 words: {profile['contractions_per_100_words']}")
    print(f"First person/100 words: {profile['first_person_per_100_words']}")
    print(f"Second person/100 words: {profile['second_person_per_100_words']}")
    print(f"Questions/100 words: {profile['questions_per_100_words']}")
    print(f"Explicit transitions/100 words: {profile['explicit_transitions_per_100_words']}")
    print(f"Long-word ratio: {profile['long_word_ratio']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or compare compact writing-style profiles.")
    parser.add_argument("sample", type=Path, help="Authentic writing sample, ideally 2-3 representative paragraphs.")
    parser.add_argument("--candidate", type=Path, help="Optional candidate text to compare with the sample.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        sample = profile_text(args.sample.read_text(encoding="utf-8"))
        if args.candidate:
            candidate = profile_text(args.candidate.read_text(encoding="utf-8"))
            result = {"reference": sample, "candidate": candidate, "comparison": compare_profiles(sample, candidate)}
        else:
            result = sample
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        elif args.candidate:
            _print_profile(sample)
            print("\nCandidate differences")
            print("---------------------")
            comparison = result["comparison"]
            if comparison["large_differences"]:
                for key in comparison["large_differences"]:
                    print(f"- {key}: delta {comparison['deltas'][key]}")
            else:
                print("- no large heuristic differences")
        else:
            _print_profile(sample)
        return 0
    except (OSError, UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
