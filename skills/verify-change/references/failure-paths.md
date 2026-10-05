# Failure Paths

Review only paths relevant to the changed boundaries.

## User/API input

- missing, empty, malformed, oversized, unexpected enum/type;
- duplicate/replayed request when relevant;
- unauthorized versus forbidden behavior.

## Network/provider

- timeout;
- transient error/retry safety;
- invalid/partial provider response;
- cancellation;
- rate limit;
- idempotency for repeated side effects.

## Persistence

- not found;
- unique/constraint conflict;
- transaction rollback/partial write;
- old data shape during migration;
- concurrency/stale update.

## UI/state

- loading, empty, error, retry;
- stale request finishing after a newer request;
- failed optimistic update;
- unmounted/cancelled operation when relevant.

## Background jobs

- duplicate delivery;
- retry/exhaustion;
- poison message;
- partial completion;
- idempotent side effects.
