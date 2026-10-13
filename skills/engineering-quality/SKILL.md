---
name: engineering-quality
description: Coordinate software work spanning multiple engineering modes such as implementation, debugging, refactoring, migration, or verification. Prefer a specific skill for single-mode work; use project-quality-orchestrator for broad audits.
---

# Engineering Quality

Coordinate a software change without loading every workflow at once. Select the smallest useful specialist set, preserve repository intent, control scope, and require honest evidence before completion.

## 1. Set rigor and pace

Classify semantic risk before choosing workflow depth:

- **L0** trivial/mechanical -> edit + smallest check;
- **L1** focused -> one specialist + targeted verification;
- **L2** shared -> inspect callers + broader tests/scope review;
- **L3** high-risk -> explicit contract + independent review + full verification;
- **L4** long-horizon -> staged checkpoints + compact handoff state.

Use [references/adaptive-rigor.md](references/adaptive-rigor.md) for escalation/de-escalation rules.

Choose **FAST**, **BALANCED** (default), or **THOROUGH** without lowering the safety floor. Use [references/workflow-budgets.md](references/workflow-budgets.md) when retry, churn, or reset limits matter.

## 2. Establish the change contract

Before substantial edits, determine:

- requested outcome and observable acceptance criteria;
- primary mode(s): build, debug, refactor, architecture, verification, or a real combination;
- explicit non-goals;
- applicable repository guidance and local precedent;
- contracts, persisted data, security boundaries, or deployment behavior that constrain the change.

Prefer existing repository conventions over new abstractions unless evidence shows they are insufficient.

Use [references/change-contract.md](references/change-contract.md) or [assets/change-plan.md](assets/change-plan.md) when a written plan helps.

## 3. Select only the modes needed now

Use [references/mode-selection.md](references/mode-selection.md) for the full routing table.

Common routing:

- new capability -> `structure-feature`;
- reproducible defect -> `debug-root-cause`;
- behavior-preserving cleanup -> `refactor-safely`;
- shared boundary/blast radius -> `guard-architecture`;
- test-cost/deferred checks -> `tiered-testing`;
- already-red baseline -> `baseline-compare`;
- intermittent test -> `flaky-test-triage`;
- repository-context uncertainty -> `context-engineering`;
- version-sensitive external behavior -> `source-grounded-development`;
- high-risk fresh-context review -> `independent-review`;
- trust/security boundary -> `security-hardening`;
- user-facing interface quality -> `ui-ux-quality`;
- controlled technical prose -> `asd-ste100-writing`;
- natural fact-preserving prose -> `humanizer-writing`;
- final readiness -> `verify-change`;
- broad source-to-consumer audit/release-freeze work -> `project-quality-orchestrator`.

Default to one specialist for the current phase. Use two only when that phase genuinely spans both concerns. Do not preload later-phase skills or turn a narrow task into a broad rewrite.

## 4. Inspect, scope, and preserve safeguards

Before changing code, identify the current owner, strongest nearby precedent, protecting tests, important callers/consumers, and generated/vendor boundaries. Search before adding a new helper, service, validator, abstraction, error type, or configuration path.

Keep a compact map:

```text
Need -> owner -> files -> contracts -> verification
```

If edits expand materially beyond the expected map, reassess instead of stacking more patches. Use [references/scope-control.md](references/scope-control.md) for escalation signals.

Do not obtain green status by silently reducing assurance. Treat weakened assertions, skipped tests, disabled checks, broad ignores, swallowed exceptions, test-only production branches, or mocks that bypass the real defect as review triggers.

## 5. Keep architecture proportional

Avoid both:

- **patch stacking** around a bad core rule;
- **ceremonial architecture** with abstractions that have no current responsibility.

Prefer the smallest structure that gives the change one clear owner and keeps likely future changes understandable.

## 6. Verify according to risk

Start with the cheapest evidence that can falsify the requirement, then broaden:

1. reproduction/focused test;
2. nearby unit/integration tests;
3. type/lint/static checks when applicable;
4. broader suite for shared/high-blast-radius code;
5. build/runtime/e2e when behavior crosses those boundaries.

Review realistic failure paths explicitly for security, auth, migration, concurrency, file/process, or externally visible API changes.

For the final completion gate use [references/completion-contract.md](references/completion-contract.md) rather than duplicating its checklist here.

## 7. Finish from the final diff and evidence

Before declaring done, inspect the final candidate for behavior, ownership, contracts, regression protection, safeguard integrity, dead/replacement code, debug residue, and stale verification.

Report:

- what changed and why;
- root cause when applicable;
- important architecture/contract decisions;
- checks actually run and their results;
- remaining risk, unavailable environment, or bounded temporary debt.

Use [references/technical-debt.md](references/technical-debt.md) when a workaround remains.

Do not state that the whole system is verified when only targeted checks were run.
