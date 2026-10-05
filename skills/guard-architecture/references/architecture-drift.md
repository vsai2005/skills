# Architecture Drift

Architecture drift is gradual loss of intended ownership/boundaries through individually convenient changes.

## Typical progression

```text
one exception
 -> copied exception
 -> shared workaround
 -> new callers rely on workaround
 -> workaround becomes de facto architecture
```

## Review questions

- Is this exception truly unique, or will others copy it?
- Could translation happen once at the boundary instead?
- Does this new dependency point in the intended direction?
- Does a shared module now know about a feature-specific concept?
- Is a compatibility concern spreading beyond the adapter/migration layer?
- Are there now two authoritative implementations of the same policy?

## Repair strategy

Correct the smallest ownership boundary that prevents repetition. Add an architecture test/lint rule only when the repository can express the rule reliably and the cost is justified.
