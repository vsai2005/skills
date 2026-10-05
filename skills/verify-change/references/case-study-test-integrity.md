# Case Study: Green Is Not Enough

## Situation

A permission regression returns 200 instead of 403. An integration test correctly fails:

```ts
expect(response.status).toBe(403);
```

Changing it to this makes CI green:

```ts
expect(response.status).toBeTruthy();
```

## Why that is not a fix

The requirement did not change. The stronger assertion is evidence that the authorization boundary is wrong. Weakening it deletes the alarm.

## Correct workflow

1. Preserve the failing test.
2. Trace where authorization is expected to happen.
3. Fix the missing/bypassed permission check at the trustworthy server boundary.
4. Add a nearby allowed-user case if useful.
5. Run targeted authorization tests and the broader affected suite.

A test should change only if the contract changed or the test itself was invalid.
