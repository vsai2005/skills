---
name: tiered-testing
description: Plan and execute software verification in cheap and heavy tiers so fast checks run continuously while expensive suites are scheduled deliberately. Use when a change needs a test strategy, when shared code increases blast radius, when heavy checks cannot run immediately, or when deferred verification must be tracked in PENDING_TESTS.md without silently being forgotten.
---

# Tiered Testing

Spend verification cost where it changes confidence, without postponing high-risk evidence until the end.

## 1. Classify checks by cost and signal

Build a small test map before substantial implementation:

- **cheap**: focused unit tests, parser/schema checks, static/type/lint checks, narrow integration tests;
- **medium**: module/package suites, representative integration tests, build checks;
- **heavy**: full e2e, large integration environments, cross-browser/device matrices, long-running migration/performance suites.

Use [references/test-tiers.md](references/test-tiers.md) for selection rules.

## 2. Run cheap checks early and repeatedly

Run the fastest relevant reproduction/check before editing when practical, then rerun after meaningful changes. Do not save all verification for the final diff.

## 3. Force an early run for shared-code changes

A cheap-looking edit becomes high-risk when it changes a shared primitive, contract, schema, auth rule, parser, persistence model, provider adapter, build/config path, or dependency used broadly.

When a shared-code trigger applies, run at least one broader representative check **before** continuing deep implementation. Use [references/shared-code-triggers.md](references/shared-code-triggers.md).

## 4. Defer heavy checks explicitly, never mentally

If a heavy check cannot run now, add it to `PENDING_TESTS.md` with:

- exact command;
- why it is deferred;
- explicit trigger for running it.

Use `scripts/pending_tests.py` when available. Follow [references/pending-tests.md](references/pending-tests.md) and [assets/PENDING_TESTS.template.md](assets/PENDING_TESTS.template.md).

## 5. Clear the queue at the trigger

Before merge/release—or earlier when the recorded trigger is reached—run the pending command, remove it only after the result is known, and preserve failures as evidence.

Do not mark a pending test complete because a different, cheaper test passed.

## 6. Escalate by evidence and blast radius

Move to heavier verification when:

- a cheap check fails unexpectedly;
- shared code changed;
- behavior crosses process/network/database/browser boundaries;
- the fix was broad or architectural;
- the failure history suggests integration-only risk.

## 7. Report what was run and what remains

Final reporting must distinguish checks actually completed from deferred checks still listed in `PENDING_TESTS.md`. For completion evidence, pair this skill with `verify-change` when available.
