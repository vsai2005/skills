#!/usr/bin/env python3
"""Dependency-free paired statistics for repeated live skill evaluations."""
from __future__ import annotations

import math
import random
import statistics
from typing import Iterable


def mean(values: Iterable[float]) -> float | None:
    vals = list(values)
    return statistics.fmean(vals) if vals else None


def median(values: Iterable[float]) -> float | None:
    vals = list(values)
    return statistics.median(vals) if vals else None


def bootstrap_mean_ci(
    values: list[float],
    *,
    confidence: float = 0.95,
    samples: int = 5000,
    seed: int = 0,
) -> tuple[float | None, float | None]:
    """Return a deterministic percentile bootstrap CI for the paired mean delta."""
    if not values:
        return None, None
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if samples < 100:
        raise ValueError("bootstrap samples must be at least 100")
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed)
    n = len(values)
    draws = []
    for _ in range(samples):
        draws.append(statistics.fmean(values[rng.randrange(n)] for _ in range(n)))
    draws.sort()
    alpha = 1.0 - confidence
    low_index = max(0, min(samples - 1, int(math.floor((alpha / 2.0) * samples))))
    high_index = max(0, min(samples - 1, int(math.ceil((1.0 - alpha / 2.0) * samples)) - 1))
    return draws[low_index], draws[high_index]


def exact_sign_test_pvalue(values: list[float], *, epsilon: float = 1e-12) -> float | None:
    """Two-sided exact sign-test p-value for paired deltas; ties are ignored."""
    positives = sum(1 for value in values if value > epsilon)
    negatives = sum(1 for value in values if value < -epsilon)
    n = positives + negatives
    if n == 0:
        return 1.0
    k = min(positives, negatives)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def win_rate(values: list[float], *, epsilon: float = 1e-12) -> float | None:
    decided = [value for value in values if abs(value) > epsilon]
    if not decided:
        return None
    return sum(1 for value in decided if value > 0) / len(decided)
