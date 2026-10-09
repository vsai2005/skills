# Security Verification

Prefer evidence at the real security boundary.

## Minimum pattern

1. Prove an authorized case still succeeds.
2. Prove at least one realistic unauthorized/hostile case fails for the intended reason.
3. Prove the control lives at the owning boundary, not only in a caller/UI.
4. Inspect logs/errors for accidental sensitive data.
5. Run broader regression checks when the boundary is shared.

## Useful evidence by boundary

- HTTP/API: real request, status, response schema/body redaction, auth context.
- Persistence: durable state before/after, transaction/idempotency behavior.
- File: canonical target path, permissions, traversal/symlink negative cases.
- Command/process: structured argv, no shell interpolation, restricted environment/cwd.
- Network: resolved/redirected target and credential-forwarding behavior.
- Browser/session: cookie flags, CSRF/origin behavior, authorization server-side.

## Do not overclaim

Passing known abuse cases is not a security proof. State what was tested, what was inspected only, and what remains environment-dependent (for example WAF/cloud IAM/runtime sandbox behavior).
