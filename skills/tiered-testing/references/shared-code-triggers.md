# Shared-Code Triggers

Run a broader representative check early when a change affects a high-fan-out owner.

Strong triggers include:

- shared validation/normalization/parsing;
- public API/event/schema types;
- auth/authz/session rules;
- database models/migrations/serialization;
- provider/plugin adapters used by multiple features;
- core state machines or concurrency primitives;
- package build/config/dependency resolution;
- code generation/templates consumed broadly.

## Early-run rule

Do not wait until the final completion gate. After the smallest coherent shared-code edit:

1. run the focused owner test;
2. run at least one representative consumer/module check;
3. inspect whether failures expand the blast radius;
4. only then continue deeper changes.

This catches a wrong shared abstraction while the diff is still small.
