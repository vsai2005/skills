---
name: engineering-quality
description: Coordinate end-to-end software changes that span more than one engineering mode, such as implementing a feature plus debugging regressions, refactoring while changing behavior, or reviewing a broad patch for architecture and verification. Use for multi-phase coding work where scope, architecture, implementation, debugging, refactoring, and final proof must be coordinated. Prefer a more specific skill for a simple single-mode task.
---

# Engineering Quality

Coordinate a software change without loading every possible rule blindly. Select the smallest useful workflow, preserve repository intent, and require honest verification before completion.

## 1. Choose the rigor level

Classify semantic risk before selecting workflow depth. Use [references/adaptive-rigor.md](references/adaptive-rigor.md):

- **L0** trivial/mechanical: edit + smallest check;
- **L1** focused: one specialist + targeted verification;
- **L2** shared: inspect callers + broader tests/scope review;
- **L3** high-risk: change contract + independent review + full verification;
- **L4** long-horizon: staged checkpoints + compact context/handoff state.

De-escalate when inspection shows the task is simpler than expected. Process overhead is a cost.

## 2. Choose pace without lowering the safety floor

Select **FAST**, **BALANCED** (default), or **THOROUGH**. Risk level defines mandatory checks; pace only changes optional depth. Use [references/workflow-budgets.md](references/workflow-budgets.md) for retry/churn reset signals.

## 3. Establish the change contract

Before substantial edits, determine:

- requested outcome and observable acceptance criteria;
- whether the task is primarily build, debug, refactor, architecture review, verification, or a real combination;
- explicit non-goals and areas that should remain unchanged;
- repository guidance that applies to touched files;
- public contracts, persisted data, security boundaries, or deployment behavior that may constrain the change.

If the repository already contains a good convention, prefer it to inventing a new one.

For larger work, use the compact planning structure in [references/change-contract.md](references/change-contract.md). When a written artifact helps, start from [assets/change-plan.md](assets/change-plan.md).

## 4. Select modes deliberately

Use [references/mode-selection.md](references/mode-selection.md) to choose only the modes needed.

Typical routing:

- New capability or extension: apply the `structure-feature` workflow.
- Reproducible defect, regression, crash, wrong output, or stable failing test: apply the `debug-root-cause` workflow.
- Behavior-preserving cleanup or decomposition: apply the `refactor-safely` workflow.
- Shared boundary, dependency direction, ownership, or high-blast-radius change: apply the `guard-architecture` workflow.
- Test-cost planning/deferred heavy checks: apply the `tiered-testing` workflow.
- Existing red checks requiring candidate-vs-baseline attribution: apply the `baseline-compare` workflow.
- Intermittent/nondeterministic tests: apply the `flaky-test-triage` workflow.
- Repository-context uncertainty/noisy long session: apply `context-engineering`.
- Version-sensitive external API/framework behavior: apply `source-grounded-development`.
- High-risk/fresh-context second review: apply `independent-review`.
- Auth, authorization, secrets, untrusted input, command/file/network boundaries, value transfer, or other attacker-controlled trust boundaries: apply `security-hardening`.
- Technical prose that needs clear controlled English: apply `asd-ste100-writing` to the prose only, not to code identifiers or quoted contracts.
- Prose that is accurate but stiff, repetitive, generic, or machine-like: apply `humanizer-writing`; for technical procedures, use it after `asd-ste100-writing` and do not undo controlled terminology or safety wording.
- Final readiness or pre-merge evidence: apply the `verify-change` workflow.

When the host exposes those skills separately, explicitly consult the selected skill's `SKILL.md` and only the references needed for that phase. When it does not, use [references/mode-selection.md](references/mode-selection.md) as the fallback summary. Do not assume another skill was loaded merely because its name is mentioned here.

Do not turn a narrow task into a broad rewrite merely because several skills are available.

## 5. Inspect before changing

Read enough of the repository to answer:

- Where does this responsibility live today?
- Which nearby implementation is the best local precedent?
- Which tests currently protect this behavior?
- Which callers/consumers depend on the affected contract?
- Are relevant files generated, vendored, or intentionally special?

Search before adding a new helper, service, validator, abstraction, error type, or configuration path.

## 6. Control scope

Maintain a mental or written change map:

```text
Need -> owner -> files -> contracts -> verification
```

When actual edits expand materially beyond the expected map, stop adding patches and reassess why. Broad scope can be correct, but it should be explainable.

Use [references/scope-control.md](references/scope-control.md) for scope-expansion signals.

## 7. Preserve safeguards

Do not obtain success by silently reducing assurance. Treat these as review triggers:

- weakening assertions or deleting edge-case tests;
- adding skipped tests;
- disabling lint/type/security rules;
- introducing broad `any`, ignores, or suppression comments;
- swallowing exceptions;
- adding test-only branches to production logic;
- replacing a failing integration path with a mock that no longer exercises the defect.

A safeguard may change when the requirement or safeguard itself is wrong. Make that reason explicit.

## 8. Keep architecture proportional

Avoid both extremes:

- **patch stacking**: more conditions, fallbacks, and special cases around a bad core rule;
- **ceremonial architecture**: interfaces, factories, layers, or directories with no current responsibility.

Prefer the smallest structure that gives the change one clear home and keeps likely future changes understandable.

## 9. Verify in layers

Use the cheapest reliable evidence first, then expand according to risk:

1. focused test or reproduction;
2. nearby unit/integration tests;
3. typecheck/lint/static checks where applicable;
4. broader suite for shared/high-blast-radius code;
5. build/runtime/e2e checks when behavior crosses those boundaries.

For security-sensitive, data-migration, concurrency, auth, file-system, command-execution, or externally visible API changes, review failure paths explicitly.

## 10. Perform a completion review

Before declaring done, inspect the final diff rather than trusting the sequence of edits.

Confirm:

- the requested behavior is implemented or defect removed;
- the final code expresses the general rule rather than only known examples;
- responsibilities remain understandable;
- no unnecessary duplicate logic or dead replacement code remains;
- public contracts changed only intentionally;
- meaningful regression coverage exists for meaningful defects;
- safeguards were preserved or justified;
- temporary debug code and accidental suppression are absent;
- verification claims match commands actually run.

Use [references/completion-contract.md](references/completion-contract.md) for the full gate.

## 11. Report evidence, not confidence

Finish with a compact summary containing:

- what changed and why;
- root cause for bug work, when applicable;
- important architecture/contract decisions;
- verification actually run and result;
- remaining risk, unverified environment, or deliberate temporary debt.

When a workaround remains, use [references/technical-debt.md](references/technical-debt.md) to record its reason, bounded scope, risk, and removal condition.

Do not state that the whole system is verified if only targeted checks were run.
