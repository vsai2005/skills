# Test Tiers

Treat cost as wall-clock/environment cost, not importance.

## Cheap

Typical examples:

- one failing reproduction;
- focused unit/contract tests;
- schema/parser fixtures;
- formatter/lint/typecheck on touched package;
- small deterministic integration test.

Run these before/after meaningful edits because feedback is fast.

## Medium

Typical examples:

- package/module suite;
- service integration suite;
- production build/type generation;
- targeted database/provider integration.

Run when the change reaches that boundary or a shared trigger fires.

## Heavy

Typical examples:

- full repository suite;
- end-to-end/browser/device matrix;
- external sandbox integration;
- long migration/replay/performance suites.

Heavy does not mean optional. If it is required but unavailable now, record it in `PENDING_TESTS.md` with a run trigger.

## Selection rule

Prefer the cheapest check that can falsify the current hypothesis, then widen when risk or evidence requires it. Do not run a huge suite merely to compensate for having no focused test.
