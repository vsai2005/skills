# Abuse-Case Checklist

Choose only relevant cases. This is not a claim that the list is exhaustive.

## Access control
- unauthenticated request;
- authenticated wrong user/tenant;
- lower privilege/expired scope;
- direct object identifier substitution;
- stale session after privilege removal;
- confused-deputy/service-account boundary.

## Input and execution
- delimiter/quote/control-character input;
- alternate encodings and normalization;
- path traversal, absolute paths, symlinks, archive entries;
- command/template/query injection;
- malformed or oversized serialized input;
- content-type mismatch and polyglot upload.

## Network
- localhost/private/link-local/metadata targets;
- redirect from allowed to forbidden target;
- unexpected schemes/ports;
- credential/header forwarding to another origin;
- slow/oversized responses.

## State and concurrency
- duplicate request/replay;
- retry after partial success;
- concurrent ownership/permission change;
- stale cache or stale authorization decision;
- idempotency-key collision/reuse.

## Information exposure
- stack trace or provider body returned to user;
- logs containing tokens/PII;
- timing/existence differences exposing protected resources;
- debug endpoints or diagnostics enabled outside intended environment.
