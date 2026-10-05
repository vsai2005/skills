# Behavior Lock

A behavior lock gives the refactor a stable target.

## Sources of truth

Use the strongest available combination:

- existing unit/integration/e2e tests;
- public API schema or interface;
- snapshot/golden outputs when appropriate;
- recorded provider interactions;
- database fixtures and migration expectations;
- explicit product requirements.

## Characterization tests

When legacy behavior has little coverage, write a test that captures important current behavior before moving code. Characterization is not an endorsement of every quirk; it prevents accidental changes while the team decides which quirks to keep.

## Avoid brittle locks

Do not freeze irrelevant implementation details. Prefer observable contracts over private call order unless call order itself matters.

Example: assert returned domain result and side effect, not that three private helper methods were called in a specific order.
