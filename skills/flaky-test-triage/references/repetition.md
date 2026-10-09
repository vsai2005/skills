# Repetition and Failure Rate

Choose N before the run and report the observed result honestly.

Example:

```text
20 comparable runs, 5 test failures -> observed failure rate 25%
```

Do not convert a finite sample into a claim about the exact long-run probability. `flake_check.py` reports a 95% Wilson interval to make sampling uncertainty visible. In particular, `0/20` means **zero observed failures in 20**, not that the true failure probability is zero.

## Size N from a historical failure rate

When CI/history gives an approximate per-run failure probability `p`, choose N for a desired probability `c` of seeing at least one failure:

```text
N >= log(1-c) / log(1-p)
```

Example: for an estimated 5% failure rate and 95% detection confidence, N is 59.

```bash
python3 scripts/flake_check.py \
  --expected-rate 0.05 \
  --detection-confidence 0.95 \
  --timeout 120 \
  -- <exact command>
```

This assumes independent runs with a stable failure probability. Treat it as planning guidance, not proof. Contention, order dependence, environment differences, and bursty failures violate that assumption.

## Keep inconclusive runs separate

Timeouts, infrastructure failures, and apparent zero-test executions are not ordinary test failures and should not be silently folded into the flake rate.

Useful options:

```bash
python3 scripts/flake_check.py \
  --runs 20 \
  --timeout 120 \
  --require-output-regex "[1-9][0-9]* passed" \
  --infrastructure-exit-code 75 \
  --zero-tests-exit-code 5 \
  --log-dir .verification/flake-auth \
  -- <exact command>
```

Child stdout/stderr is captured so `--json` remains valid JSON. Failure signatures include both channels, preventing a shared warning on stderr from hiding different failures on stdout. Per-run logs and representative signature excerpts can be retained for analysis. Per-run timeouts terminate the command process group/tree on supported platforms so descendants do not keep contaminating later repetitions.

## Useful comparisons

Keep N and the command comparable across:

- before versus after fix;
- isolated versus full-suite context;
- serial versus parallel execution;
- fixed seed/order versus randomized seed/order;
- local versus the failing CI operating system/runtime;
- low-contention versus production-like/shared-resource load.

If local attempts remain clean while the historical failure exists only on one CI/OS combination, move the experiment to that environment instead of multiplying local runs indefinitely.
