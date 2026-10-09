# Runtime Validation

Static checks and unit tests are not enough when the requirement crosses a runtime boundary.

## Web / UI

Verify the relevant interaction in the actual rendered app when feasible. Inspect console errors, network calls, DOM/state, accessibility-relevant behavior, and the user-visible result. Use visual evidence only when appearance is part of the requirement.

## API / service

Exercise a real request path. Check status, headers, schema/body, authorization context, error behavior, and downstream/persisted effect where applicable.

## CLI / process

Check exit status, stdout/stderr contract, created/modified files, environment/cwd assumptions, and failure behavior.

## Database / persistence

Verify durable state before/after, transaction behavior, constraints, migrations/rollback where relevant, and concurrent/idempotent behavior for shared state.

## Async / events / queues

Verify producer and consumer behavior, retry/duplicate delivery, idempotency, ordering assumptions, and final observable state.

## Evidence rule

Do not claim runtime behavior is verified if only source/tests were inspected. Record the actual command or runtime observation in the evidence ledger when possible.
