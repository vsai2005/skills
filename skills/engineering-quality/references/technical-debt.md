# Technical-Debt Accounting

Sometimes the safest change is a deliberate workaround: an upstream bug cannot be fixed locally, a migration must support an overlap window, or a release deadline requires containment before a deeper repair.

The problem is not the existence of temporary debt. The problem is invisible, ownerless debt that looks permanent after the context is forgotten.

## Record a workaround when all are true

- the ideal/root-cause solution is currently unsafe, unavailable, or outside scope;
- the workaround has a bounded location and behavior;
- the tradeoff is understood;
- there is a concrete condition under which it can be removed or revisited.

## Minimum record

```text
Temporary debt:
Reason:
Scope/location:
Risk:
Removal condition:
Verification:
```

Example:

```text
Temporary debt: normalize provider v3 empty payload as retryable once.
Reason: upstream SDK v3.8 can return an empty first response after reconnect.
Scope/location: AcmeProviderAdapter only.
Risk: one extra request on the affected reconnect path.
Removal condition: remove after minimum supported SDK >= 3.9 and provider issue ACME-1842 is verified fixed.
Verification: adapter tests cover empty-first-response and non-idempotent calls are excluded from retry.
```

## Avoid vague debt markers

Weak:

```text
TODO: clean this later
```

Better:

```text
Compatibility shim for v1 event consumers. Remove after consumer-a and
consumer-b are deployed on schema v2; tracked by migration issue #123.
```

## Do not use debt accounting to excuse unsafe behavior

A note does not make an authorization bypass, data-loss path, secret exposure, or destructive migration acceptable. High-risk temporary behavior still requires an appropriate safety decision.
