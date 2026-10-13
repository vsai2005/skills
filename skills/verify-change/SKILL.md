---
name: verify-change
description: Perform final or pre-merge verification of a completed software change using actual evidence. Check regressions, test integrity, failure paths, risks, and leftovers. Not for a broad source-to-consumer audit.
---

# Verify Change

Treat "done" as an evidence claim bound to the current candidate.

## 1. Re-read the request and final diff

Compare the final code with the requested outcome and acceptance criteria. Identify intended/unchanged behavior, touched contracts, changed tests, and unexpected files. Do not trust the implementation narrative when the diff can answer the question.

## 2. Protect test and safeguard integrity

Before celebrating green, check whether the change weakened the evidence.

Use [references/test-integrity.md](references/test-integrity.md) for skips, weaker assertions, bypassing mocks, inflated sleeps/timeouts, changed fixtures, or removed checks.

For a high-value regression test, [references/mutation-probe.md](references/mutation-probe.md) can provide an isolated test-the-test probe. Use [references/case-study-test-integrity.md](references/case-study-test-integrity.md) when an example is useful.

## 3. Build evidence, then verify by risk

For non-trivial work, register readiness checks with [references/evidence-ledger.md](references/evidence-ledger.md) and `scripts/evidence_ledger.py` when available.

Run the cheapest evidence that can falsify the requirement, then broaden:

1. original reproduction/targeted tests;
2. owning-module tests;
3. static/type/lint checks;
4. broader suite for shared code;
5. build/runtime/e2e when behavior crosses those boundaries.

A check is not verified unless it ran successfully against the relevant current state.

## 4. Inspect failure, trust, performance, and residue

Use [references/failure-paths.md](references/failure-paths.md) and [references/runtime-validation.md](references/runtime-validation.md) when runtime boundaries matter.

For auth, permissions, untrusted input, file/process/network boundaries, secrets, parsing, value transfer, or destructive persistence, use [references/security-performance.md](references/security-performance.md). Apply `security-hardening` when the trust boundary itself needs design/rework.

Check obvious performance risks such as N+1 calls, repeated work in hot loops/render paths, whole-dataset loads, unbounded retries/queues/caches, or duplicate requests. Do not invent speculative micro-optimizations.

Inspect the diff for dead replacement paths, temporary logs, commented experiments, unfinished required TODOs, broad suppressions/ignores, duplicate rules, and ownerless compatibility hacks.

## 5. Require independence only when risk justifies it

For security, public contracts, persistence migrations, architecture changes, or similarly high-blast-radius work, require a fresh `independent-review` pass when the workflow supports it.

Confirm any review evidence still matches the current diff. Do not add an independent reviewer to trivial edits merely for process.

## 6. Apply the completion gate and report

Use [references/completion-gate.md](references/completion-gate.md). A failed gate means fix the issue or report the remaining risk; do not hide it.

Build `Verified` / `Not verified` from the evidence ledger, including outstanding `PENDING_TESTS.md` items. Evidence is not verified when stale, unbound to current Git state, or produced by a command that changed the candidate without an allowed state transition.

Use [assets/completion-report.md](assets/completion-report.md) for repeatable handoff.

Do not say "all tests pass" when only targeted checks ran, and do not move a failed command into `Verified`.
