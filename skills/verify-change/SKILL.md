---
name: verify-change
description: Perform a rigorous final verification or pre-merge review of a software change, checking correctness evidence, regression coverage, test integrity, type/lint suppression, failure paths, security-sensitive behavior, obvious performance risks, dead/debug code, architecture drift, and honest reporting. Use after implementation or when asked whether a patch is ready, safe, complete, or well-structured.
---

# Verify Change

Treat "done" as an evidence claim, not a feeling.

## 1. Re-read the request and final diff

Verify the final code against the original outcome and acceptance criteria. Do not rely only on the implementation narrative; patches often drift during debugging.

Identify:

- intended changed behavior;
- intentionally unchanged behavior;
- touched contracts/boundaries;
- newly added/modified tests;
- unexpected files in the diff.

## 2. Check test integrity before celebrating green

Inspect whether tests or checks were weakened.

Review for:

- deleted edge cases;
- broader/weaker assertions;
- new skips/xfails;
- mocks that bypass the defect path;
- inflated timeouts/sleeps;
- removed type/lint/security checks;
- changed fixtures that merely stop reproducing the bug.

Use [references/test-integrity.md](references/test-integrity.md). For high-value new regression tests, optionally use the isolated [test-the-test mutation probe](references/mutation-probe.md). For a concrete example of why a greener but weaker assertion is not a fix, see [references/case-study-test-integrity.md](references/case-study-test-integrity.md).

## 3. Build the verification evidence ledger

For non-trivial changes, register the checks that should prove readiness, then run or record them through `scripts/evidence_ledger.py` when available. This prevents a final summary from relying on memory.

Use [references/evidence-ledger.md](references/evidence-ledger.md).

## 4. Run risk-proportionate verification

Use a layered sequence:

1. original reproduction/targeted tests;
2. tests for the owning module;
3. static/type/lint checks;
4. broader suite for shared code;
5. build/runtime/e2e checks when the change crosses those boundaries.

Do not claim a check passed without running it successfully in the current environment.

## 5. Review failure paths

Use [references/failure-paths.md](references/failure-paths.md) for applicable boundaries. Focus on realistic failure behavior, not exhaustive hypothetical branches.

When behavior crosses a runtime boundary, use [references/runtime-validation.md](references/runtime-validation.md) and record actual runtime evidence.

## 6. Review security and data boundaries

Apply additional scrutiny when touched code handles:

- authentication/authorization/session state;
- untrusted input or uploads;
- file paths or shell/process execution;
- SQL/query construction;
- secrets/tokens;
- SSRF-capable URLs/network access;
- deserialization/parsing;
- payment/value transfer;
- migrations/destructive writes.

Use [references/security-performance.md](references/security-performance.md). For a substantive trust-boundary change, apply the dedicated `security-hardening` workflow instead of treating this final checklist as the security design process.

## 7. Review obvious performance regressions

Look for changes such as:

- N+1 queries/API calls;
- repeated parsing/computation inside loops or render paths;
- loading whole datasets/repositories when a bounded query is possible;
- unbounded retries/queues/cache growth;
- unnecessary rerenders or duplicate network requests.

Do not optimize speculative micro-performance without evidence.

## 8. Inspect maintainability residue

Search the diff for:

- dead old path after replacement;
- temporary logs/prints;
- commented-out experiments;
- TODO/FIXME introduced as unfinished required behavior;
- broad `any`, ignore, suppression, or lint disable;
- duplicate helper/rule;
- compatibility hack with no owner/removal condition.

## 9. Require fresh independent review for high-risk changes

For authentication/security, public contracts, persistence migrations, architecture changes, or other high-blast-radius work, require an `independent-review` pass before the final completion gate when the host/workflow supports it. If review-state evidence exists, confirm that it is still bound to the current diff. Treat unresolved critical/important findings as not ready. Do not require a separate reviewer for trivial edits merely to satisfy process.

## 10. Apply the completion gate

Use [references/completion-gate.md](references/completion-gate.md). A failed gate should result in a fix or an explicit remaining-risk statement, not a hidden pass.

## 11. Build the completion report from evidence

Generate the `Verified` / `Not verified` sections from the ledger instead of reconstructing them from memory. The report must include outstanding `PENDING_TESTS.md` items. Evidence is not `Verified` when it is stale, externally recorded, unbound to Git state, or produced by a command that mutated the candidate without an explicit state-change allowance. Then add static inspection and remaining-risk notes around that evidence.

For repeatable handoff, use [assets/completion-report.md](assets/completion-report.md).

Do not say "all tests pass" when only targeted tests ran, and do not move a failed command into `Verified`.
