# Design Principles

## 1. Progressive disclosure

Skill discovery should be cheap. The name and description should be enough for an agent to decide whether a skill is relevant. The main `SKILL.md` contains the essential workflow; deep patterns and edge cases stay in `references/` until they are needed.

This prevents a common failure in agent configuration: solving inconsistency by injecting a huge permanent prompt that consumes context and creates conflicting instructions.

## 2. Decisions over slogans

"Write clean code" is too vague. Useful instructions change an engineering decision:

- search for an existing abstraction before adding another one;
- reproduce a bug before changing logic when reproduction is feasible;
- do not weaken an assertion solely to make a failing test pass;
- distinguish a public contract change from an internal refactor;
- inspect callers before modifying a shared primitive;
- mark a deliberate temporary workaround with a removal condition.

## 3. Repository-native by default

The skill should not force feature folders, hexagonal architecture, dependency injection, repositories, services, or any other pattern into every project. It should first understand what the repository already does well.

A new architecture is justified only when the current structure cannot express the change cleanly or when the task explicitly includes architecture work.

## 4. Root-cause debugging

A passing test suite is evidence, not a root-cause explanation. A bug workflow should distinguish:

- symptom;
- triggering input or state;
- incorrect assumption/invariant;
- defective rule or boundary;
- fix;
- regression protection.

The agent may use a containment workaround when the real fix is unsafe or external, but should label that tradeoff instead of pretending the workaround removed the cause.

## 5. Behavior lock before structural change

Refactoring should preserve behavior by default. When important behavior is insufficiently covered, characterize it first with focused tests or another reliable observation mechanism. This reduces the chance that cleanup silently becomes a product change.

## 6. Tests are part of the contract

Tests should be updated when requirements change or when the previous test was incorrect. They should not be relaxed because production code is inconvenient to fix.

Examples of suspicious test changes include:

- replacing exact behavior checks with broad truthiness;
- removing an edge case without a requirement change;
- turning a deterministic test into a skipped test;
- mocking away the layer where the regression occurs;
- increasing timeouts to hide a race without understanding it.

## 7. Heuristics remain heuristics

Large-file thresholds, changed-file counts, `any` detection, and similar static signals are not universal rules. Generated files and domain-heavy modules can be legitimately large. A scanner finding should trigger review, not automatic refactoring.

## 8. No invisible verification

Agents should report what was actually run. If a full integration environment is unavailable, say so and distinguish:

- verified locally;
- inspected statically;
- inferred from code;
- not verified.

## 9. Provider-neutral core

The core skill instructions avoid product-specific commands when the behavior is general. Host metadata and installation instructions live in dedicated manifests/docs. This keeps one source of truth usable across Agent Skills compatible environments.
