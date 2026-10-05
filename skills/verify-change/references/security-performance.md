# Security and Performance Sanity Review

This is a focused change review, not a substitute for dedicated security or performance testing.

## Security prompts

- Is authorization checked at a trustworthy server/domain boundary, not only hidden in UI?
- Is untrusted input validated before sensitive operations?
- Are file paths normalized/restricted against traversal when needed?
- Are shell commands constructed safely without untrusted interpolation?
- Are SQL/database queries parameterized or safely generated?
- Are secrets excluded from logs/errors/client bundles?
- Can user-controlled URLs reach internal services unexpectedly?
- Are parsers/deserializers bounded and appropriate for untrusted input?

## Performance prompts

- Did a query move inside a loop?
- Did a component gain a repeated expensive computation/network call?
- Did a bounded read become full-table/full-repository loading?
- Are retries/backoff bounded?
- Did cache/collection growth become unbounded?
- Did an algorithmic path change materially for large input?

Escalate to specialized tooling when the risk is high or evidence is insufficient.
