---
name: guard-architecture
description: Review or guide architecture-sensitive software changes involving module/package boundaries, shared domain rules, dependency direction, public APIs, persistence models, providers, plugins, auth boundaries, concurrency, or broad blast radius. Use when a change risks architecture drift, circular dependencies, misplaced ownership, compatibility breakage, or cross-cutting technical debt.
---

# Guard Architecture

Protect ownership and dependency boundaries without imposing a fashionable architecture on every codebase.

## 1. Reconstruct the existing architecture

Inspect real imports/calls/data flow and repository guidance. Identify:

- primary modules/packages/features;
- allowed dependency direction;
- shared domain/infrastructure layers;
- external system boundaries;
- public contracts and persistence boundaries;
- known generated/vendor areas.

Do not judge architecture from the directory tree alone.

## 2. Identify the rule owner

For each important behavior affected by the change, answer:

- Who owns this policy?
- Who is allowed to depend on that owner?
- Who should translate external/framework/provider representations?
- Is this shared because it is semantically shared, or only because two files look similar?

Use [references/dependency-boundaries.md](references/dependency-boundaries.md).

## 3. Trace blast radius

Inspect direct and meaningful indirect consumers before changing a shared primitive. Consider:

- compile-time imports;
- runtime dispatch/registration;
- API/event consumers;
- database readers/writers;
- config/env behavior;
- tests/fixtures that encode the contract;
- deployment overlap and rollback.

Use [references/blast-radius.md](references/blast-radius.md).

## 4. Detect architecture drift

Common drift signals:

- UI/transport types imported into core domain logic;
- feature-specific logic added to global shared utilities;
- multiple modules each translating the same provider quirk;
- circular dependencies solved with dynamic imports or global registries;
- shared services becoming grab-bags of unrelated responsibilities;
- direct database/provider access bypassing an established boundary;
- compatibility branches leaking into many callers.

See [references/architecture-drift.md](references/architecture-drift.md).

## 5. Prefer local repair before redesign

If one boundary violation can be corrected locally, do that. Do not redesign the whole system because a single bad import exists.

A broader architecture change is justified when the current boundary cannot support the requested behavior cleanly, or repeated violations show the existing ownership model is no longer valid.

## 6. Protect contracts during boundary changes

For public APIs, stored data, events, plugin interfaces, or provider abstractions, identify compatibility expectations explicitly.

Use adapters/migrations where needed. Avoid making every internal call site understand both old and new formats.

## 7. Verify dependency behavior

Where tooling exists, run package/module dependency checks, type/build checks, and targeted integration tests. Also inspect the final diff for new reverse imports, cycles, or duplicated boundary translation.

## 8. Produce actionable architecture findings

For substantial reviews or handoff, use [assets/architecture-review.md](assets/architecture-review.md).

For review tasks, prioritize findings by consequence:

- correctness/security/data-loss risk;
- contract/compatibility risk;
- architecture drift likely to spread;
- maintainability issue with bounded impact;
- optional improvement.

Tie every finding to a specific boundary or ownership rule. Avoid generic architecture commentary.
