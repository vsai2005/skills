---
name: flaky-test-triage
description: Investigate intermittent tests by measuring failures and isolating order, contention, timing, or state causes. Use for flaky CI or tests that pass on rerun; do not mask causes with longer timeouts.
---

# Flaky Test Triage

Measure nondeterminism before changing it.

## 1. Freeze the failing command

Start from the exact command/test selection that exhibited flakiness. Record relevant runtime, worker count, seed/order configuration, and environment.

## 2. Run it N times and report the rate

Choose an explicit repetition count appropriate to cost; do not say "seems flaky" after two attempts. If historical CI data provides an approximate failure rate, size N for a useful chance of observing at least one failure:

```bash
python3 scripts/flake_check.py --expected-rate 0.05 --detection-confidence 0.95 --timeout 120 -- <exact command>
```

Or choose N directly when cost/history requires it:

```bash
python3 scripts/flake_check.py --runs 20 --timeout 120 -- <exact command>
```

For repetition counts, comparable-run handling, and sampling uncertainty, use [repetition guidance](references/repetition.md). Keep timeout/infrastructure/zero-test runs separate from ordinary failures, and do not count "no tests selected" as a passing or failing run.

## 3. Compare isolation versus suite/order

Run the test alone and in the suite/context where it flakes. Check whether ordering, randomized seed, previous tests, worker scheduling, operating system, runtime version, or CI-only configuration changes the rate. Escalate to the failing CI/OS environment when local evidence cannot reproduce the observed class of failure.

## 4. Check shared-resource contention

When order, shared state, or contention is plausible, inspect mutable globals, temp paths, ports, databases, caches, files, clocks, rate limits, worker pools, and cleanup with [order/contention guidance](references/order-and-contention.md).

## 5. Form and test a causal hypothesis

Examples:

- missing await/settlement;
- race between producer/consumer;
- test leaks global state;
- fixed shared resource collides in parallel;
- stale external fixture;
- nondeterministic iteration/order dependency.

Change one causal factor at a time and rerun the same repetition method.

## 6. Never "fix" by raising timeouts

A higher timeout may alter a legitimate product requirement, but it is not a flake root-cause fix. Do not increase sleeps/timeouts merely to reduce observed failures. If timing budget genuinely changed, justify it separately after the nondeterminism is understood.

## 7. Confirm the improvement statistically

Rerun N times after the fix, preferably at the same or greater N. Report before/after rates and any remaining failures. A result such as `0/20` means zero observed failures in that sample, not proof of a zero true flake rate. Do not count zero-test or infrastructure runs as successful evidence.

For substantial triage, use [assets/flake-report.md](assets/flake-report.md).
