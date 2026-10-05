---
name: debug-root-cause
description: Diagnose and fix software bugs, regressions, flaky behavior, incorrect outputs, crashes, and failing tests by reproducing the problem, isolating the defective assumption or rule, choosing the smallest correct fix, and adding regression protection. Use when a coding task is primarily about repairing behavior rather than adding a new capability.
---

# Debug Root Cause

Fix the defective rule or boundary without accumulating symptom-specific branches.

## 1. Preserve the bug as evidence

Capture the failing input, state, request, test, stack trace, or user-visible behavior before changing code when feasible.

Prefer the smallest reliable reproduction. If the supplied test already reproduces the bug, use it; do not rewrite it immediately. For substantial incidents or team handoff, use [assets/bug-fix-record.md](assets/bug-fix-record.md).

## 2. Separate symptom from cause

Write or infer a compact causal chain:

```text
Trigger -> observed path -> violated assumption/invariant -> defective rule -> symptom
```

Do not call a location the root cause merely because the exception occurs there.

Use [references/root-cause-playbook.md](references/root-cause-playbook.md) for systematic narrowing.

## 3. Inspect the owner and blast radius

Before patching, identify:

- which module actually owns the rule;
- all meaningful callers/consumers of the shared code;
- whether the failure comes from bad data, bad classification, stale state, concurrency, integration behavior, or incorrect expectations;
- whether similar workaround branches already exist.

A shared primitive may justify a slightly larger but more general fix than the failing caller.

## 4. Reject patch stacking

Treat these as high-risk debugging patterns:

- hardcoding each reported failing value;
- adding another `if` around a flawed classifier/parser;
- swallowing the exception and returning a default;
- retrying without understanding whether the operation is safe/idempotent;
- broadening a type to `any` or nullable just to silence a failure;
- disabling a validator/security check because a legitimate request failed;
- changing the test to match current broken behavior.

See [references/bug-fix-antipatterns.md](references/bug-fix-antipatterns.md).

## 5. Choose the smallest correct fix

A correct fix should change the rule at its natural owner and explain the original failure.

Prefer:

```text
one corrected classification boundary
```

over:

```text
six special cases at six call sites
```

Do not broaden scope into unrelated cleanup. If required cleanup is necessary to express the fix safely, keep it behavior-preserving and focused.

## 6. Add regression protection

For a meaningful defect, add or strengthen a test that:

- fails for the original bug before the fix;
- passes for the intended general behavior after the fix;
- sits close enough to the defective owner to diagnose future regressions;
- includes nearby negative/edge cases when overfitting is plausible.

Use [references/regression-testing.md](references/regression-testing.md). For a worked example of fixing the owning rule rather than reported values, see [references/case-study-classifier-root-cause.md](references/case-study-classifier-root-cause.md).

## 7. Verify the neighborhood

Run the original reproduction first, then relevant nearby tests/checks. Expand to broader suites when the changed rule is shared or high risk.

When a fix touches auth, security, persistence, concurrency, protocol parsing, public API, or migrations, verify relevant failure paths and compatibility.

## 8. Inspect the final diff for debugging residue

Remove:

- temporary logging/prints;
- commented experimental code;
- temporary timeouts or sleeps;
- unused workaround branches;
- accidentally weakened assertions;
- skipped tests introduced during investigation.

## 9. Report the causal result

State:

- observed bug;
- root cause;
- corrected rule/location;
- regression coverage;
- verification actually run;
- any remaining uncertainty.

If only a containment workaround was possible, call it a workaround and record why the actual cause was not changed.
