---
name: refactor-safely
description: Refactor, simplify, split, reorganize, modernize, or remove duplication from existing code while preserving intended behavior and public contracts. Use for cleanup of large files, tangled responsibilities, legacy modules, duplicated logic, dependency cleanup, naming/structure improvements, or migrations where structural change is primary and behavior should remain stable unless explicitly requested.
---

# Refactor Safely

Improve structure without using "cleanup" as permission for uncontrolled behavior change.

## 1. Define the preservation boundary

Identify what must remain stable:

- public APIs, routes, events, CLI output, or component props;
- persisted data and migration behavior;
- observable user flows;
- performance/ordering guarantees that callers depend on;
- error semantics where they are part of the contract.

If the task intentionally changes behavior, separate that change from the behavior-preserving refactor as clearly as practical.

## 2. Lock important behavior

Before moving logic, find existing tests that characterize the area. When coverage is weak and the behavior matters, add focused characterization tests or another reliable observation method before restructuring.

Use [references/behavior-lock.md](references/behavior-lock.md). For larger work, capture the sequence and preservation boundary with [assets/refactor-plan.md](assets/refactor-plan.md).

## 3. Identify the structural problem

Name the debt precisely. Examples:

- one component owns unrelated state machines and presentation;
- repeated normalization exists in four routes;
- provider-specific behavior leaked into domain code;
- a service imports UI-layer types;
- a "manager" class owns validation, persistence, retries, and formatting;
- a legacy adapter remains after migration.

Do not refactor merely because a different personal style is possible.

## 4. Choose a destination architecture before moving code

Decide where each responsibility should live, using existing repository conventions when they are sound.

A refactor should reduce ambiguity about ownership. If the proposed destination creates more layers but no clearer owner, reconsider it.

See [references/refactoring-strategies.md](references/refactoring-strategies.md). For an end-to-end decomposition example, see [references/case-study-component-refactor.md](references/case-study-component-refactor.md).

## 5. Refactor in small semantic steps

Prefer changes that can be reasoned about independently:

1. characterize behavior;
2. rename/expose seams if needed;
3. extract one coherent responsibility;
4. reroute callers;
5. run focused checks;
6. remove the old path when no longer used;
7. repeat.

Avoid simultaneously rewriting logic, changing API shape, changing storage, and changing tests unless the task truly requires a migration. If contracts or persisted data must evolve, follow [references/migration-and-contracts.md](references/migration-and-contracts.md).

## 6. Protect dependency direction

When moving code, ensure the new location does not introduce reverse imports or circular dependencies. Shared abstractions should depend on stable lower-level concepts rather than feature UI or transport details.

For package/boundary-sensitive refactors, use `guard-architecture` if available.

## 7. Remove migration debris

After callers move, search for:

- dead old implementation;
- compatibility aliases no longer needed;
- duplicate types/schemas;
- unused exports/imports;
- stale comments/docs;
- obsolete feature flags;
- tests that exercise only the removed path.

Do not leave both architectures indefinitely unless compatibility explicitly requires it.

## 8. Verify equivalence and improvement

Run behavior-lock tests after each meaningful step. At completion, confirm both:

**Preservation:** required behavior/contracts still hold.

**Improvement:** the named structural debt actually decreased.

A refactor that adds wrappers while leaving the original god object untouched is not complete.

## 9. Report the refactor honestly

Summarize:

- structural problem addressed;
- preservation boundary;
- important moves/extractions;
- behavior intentionally changed, if any;
- checks run;
- remaining compatibility/debt.
