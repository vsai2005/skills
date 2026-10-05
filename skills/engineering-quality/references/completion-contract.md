# Completion Contract

A software change is complete only when its evidence and maintainability are proportionate to risk.

## Required questions

### Correctness

- Does the changed behavior satisfy the request?
- For a defect, would the original reproduction fail before and pass after?
- Does the fix cover the rule, not only provided examples?

### Structure

- Is each new responsibility placed with a clear owner?
- Did the change add unnecessary layers or duplicate logic?
- Did any touched unit become materially harder to understand or test?

### Contracts

- Were public APIs, events, schemas, persisted data, routes, CLI behavior, or config semantics changed?
- If yes, is compatibility/migration intentional and tested?

### Safeguards

- Were tests, type checks, validation, authorization, or lint rules weakened?
- Are ignores/suppressions newly introduced and justified?
- Are skipped tests or debug branches present?

### Failure behavior

When relevant, check invalid input, null/empty state, timeout, cancellation, partial failure, permission denial, dependency failure, and retry/idempotency behavior.

### Evidence

- Which commands were actually run?
- Did they pass?
- What could not be verified in this environment?

### Debt

If a workaround remains, record its reason, scope, and removal condition. Do not hide it as a normal implementation choice.
