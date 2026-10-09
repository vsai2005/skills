# Runtime Observability

Use runtime evidence when static reading cannot distinguish competing causes. Instrument boundaries and state transitions rather than flooding every line with logs.

## Browser and UI bugs

Inspect, when available:

1. console/runtime exceptions;
2. network requests, status codes, payload shape, retries, and timing;
3. DOM/component state at the failure boundary;
4. storage/cache state;
5. a performance trace when the symptom is latency, jank, or excessive rendering.

Reproduce the real user path. A component-level unit test is not a substitute when the bug depends on browser state, routing, or network behavior.

## Backend and API bugs

Correlate one request across:

- request/correlation ID;
- validated input;
- auth/authorization decision;
- service/repository boundary;
- dependency calls and retries;
- response/error translation.

Log state transitions and identifiers, not secrets or full sensitive payloads.

## Database and persistence bugs

Inspect:

- executed query and bound parameter *shape*;
- transaction/isolation state;
- read/write ordering;
- constraint/locking failures;
- execution plan for performance issues;
- migration/schema version when compatibility matters.

Do not print credentials or sensitive row data merely to prove a query ran.

## Distributed and asynchronous bugs

Correlate across boundaries using stable IDs. Check:

- duplicate delivery/idempotency;
- retry policy and backoff;
- timeout/cancellation propagation;
- queue ordering;
- stale caches;
- worker ownership/lease expiry;
- clock assumptions;
- partial success across services.

A retry that makes the symptom disappear is evidence, not a root-cause fix.

## Evidence quality

Prefer observations that exercise the actual producer/caller path. If a probe bypasses the path under investigation, state that limitation explicitly.
