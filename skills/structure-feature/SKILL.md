---
name: structure-feature
description: Build or extend software features in an existing repository while preserving clean ownership, repository conventions, modular responsibilities, reusable domain logic, and proportional complexity. Use when implementing endpoints, UI flows, services, modules, integrations, data handling, or other new capability where code placement and maintainability matter.
---

# Structure Feature

Add capability without turning the repository into a collection of one-off patches or unnecessary layers.

## 1. Learn the local shape

Before creating files, inspect:

- repository guidance and package boundaries;
- one or two nearby features that represent current good practice;
- how routing, domain logic, data access, validation, errors, types, logging, and tests are normally organized;
- existing helpers/services/components that may already own part of the responsibility.

Do not infer architecture only from folder names. Read representative code.

## 2. Define the responsibility

State the feature in terms of responsibilities rather than files.

Example:

```text
UI collects account settings.
Application logic validates and coordinates the update.
Repository/provider layer persists it.
Shared domain rule normalizes the display name.
```

Then map responsibilities to existing owners. Create a new owner only when the repository has no appropriate one.

Use [references/file-placement.md](references/file-placement.md) when ownership is unclear.

## 3. Choose proportional structure

Keep a tiny feature tiny. Split when separation improves ownership, testing, or reuse.

Avoid both:

- one giant route/component/service that performs every layer;
- a directory tree full of interfaces and wrappers with only one trivial implementation.

Use [references/complexity-budgets.md](references/complexity-budgets.md) as review triggers, not hard laws.

## 4. Keep boundaries visible

Prefer explicit flow:

```text
input -> validation -> use-case/domain decision -> side effect -> result -> presentation
```

Do not bury business rules in rendering code, database query fragments, error formatting, or test fixtures simply because that is the shortest edit.

Framework-specific details are in [references/architecture-patterns.md](references/architecture-patterns.md). For a worked account-settings example that avoids a god route, see [references/case-study-feature-structure.md](references/case-study-feature-structure.md).

## 5. Reuse before duplicating

Before adding a helper, search for:

- same normalization/validation rule;
- same API/provider call;
- same error translation;
- same UI primitive;
- same persistence query;
- same type/schema.

Reuse only when semantics are genuinely the same. Do not force unrelated concepts into a generic helper to avoid a few duplicated lines.

## 6. Design failure behavior with the happy path

For each external boundary or user input, consider relevant failures during implementation rather than after tests fail:

- invalid input;
- missing/empty state;
- unauthorized/forbidden access;
- dependency/network failure;
- timeout/cancellation;
- duplicate request/idempotency;
- partial writes/transactions;
- stale state or concurrency.

Only implement branches that are meaningful for the feature and architecture.

## 7. Test at the owner of the behavior

Place tests where they fail for the right reason.

- domain rule -> unit/domain test;
- HTTP contract -> API/integration test;
- UI interaction -> component/e2e test as appropriate;
- persistence mapping -> repository/integration test when the database behavior matters.

Avoid testing a business rule only through a giant e2e path when a focused test can lock it directly.

## 8. Review the final shape

Before completion, ask:

- Did a touched file acquire a second unrelated reason to change?
- Did a new global utility become a dumping ground?
- Is business logic trapped in UI/framework code?
- Did the feature create a second way to do something the repo already standardized?
- Did any abstraction appear before it has a real responsibility?
- Can another developer identify the owner of each important rule quickly?

Then run appropriate targeted and broader checks. For final readiness, apply the `verify-change` workflow if available.
