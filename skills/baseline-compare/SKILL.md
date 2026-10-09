---
name: baseline-compare
description: Compare failing tests or checks against a clean baseline so every current failure is classified as pre-existing or regression. Use when a repository already has red tests, an environment is noisy, a broad change exposes unrelated failures, or a reviewer needs proof that new failures were not introduced. Prefer an isolated git worktree baseline and document every manual baseline reconstruction change.
---

# Baseline Compare

Do not treat an already-red repository as either automatically safe or automatically caused by the current patch.

## 1. Define the exact comparison

Use the same:

- test/check command;
- relevant environment/configuration;
- dependency/runtime version when controllable;
- failure identity/signature rules.

Changing the command between baseline and candidate invalidates the classification.

## 2. Prefer a git worktree baseline

When Git history is available, create an isolated worktree at the comparison ref and run the same command there. This avoids mutating the candidate tree and reduces hidden baseline drift.

Follow [references/worktree-baseline.md](references/worktree-baseline.md).

## 3. Capture both failure inventories

Record stable failure identities such as test node IDs, check names, file/package/suite context, or explicit failure signatures. Avoid classifying only by aggregate counts, and disambiguate same-named tests from different modules when the runner exposes that metadata.

When available, use `scripts/baseline_diff.py` to compare inventories. Use [references/failure-inventory.md](references/failure-inventory.md) for identity/signature rules and supported formats.

## 4. Classify every current failure

Each current failure must be labeled:

- **pre-existing**: the same failure identity and available signature exist on the clean baseline;
- **regression**: the failure is new **or the same ID now fails with a different/unproven signature**.

Also note baseline failures that disappeared; they may indicate an intentional fix or an accidental loss of coverage.

## 5. If a manual baseline is unavoidable, list every change

Sometimes the historical ref cannot run unchanged because dependencies, fixtures, or infrastructure no longer exist. If rebuilding the baseline manually, enumerate **every** modification made to get it running and explain why it should not affect the failure being classified.

Use [references/manual-baseline.md](references/manual-baseline.md) and [assets/baseline-report.md](assets/baseline-report.md).

## 6. Treat uncertain equivalence as unknown, not pre-existing

If the baseline environment differs materially or a failure signature is ambiguous, do not use "pre-existing" as a confidence shortcut. Record the limitation and investigate further.

## 7. Report the comparison

Include:

- baseline ref/source;
- exact command/environment;
- pre-existing failures;
- regressions;
- baseline-only/resolved failures;
- any manual baseline modifications;
- equivalence limitations.
