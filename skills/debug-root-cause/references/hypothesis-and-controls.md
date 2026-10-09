# Hypotheses, Decision Signals, and Controls

Do not edit code merely because a cause sounds plausible. State what observation would support or reject the hypothesis before the experiment.

## Compact experiment record

```text
Hypothesis:
Prediction if true:
Prediction if false:
Known-good control:
Experiment:
Observation:
Conclusion: confirmed / rejected / inconclusive
```

Use the smallest experiment that separates competing explanations. Change one causal factor at a time when practical.

## Prefer a known-good control

Compare the failing case with something that should work under the same conditions:

- working input versus failing input;
- same request with cache bypassed versus cached;
- serial versus parallel execution;
- clean database state versus contaminated state;
- old release versus suspected regression release;
- same dependency call with validated configuration.

A control helps distinguish the suspected cause from unrelated environmental noise.

## Proximate failure is not automatically the root cause

An error can truthfully describe the immediate failure while pointing attention at the wrong layer.

Example:

```text
mock.method() is missing
```

Before adding the missing mock method, ask whether the mocked path should have executed at all. The real defect may be an earlier routing/state error.

For every proposed fix, answer:

1. Should this failing path be reachable for the triggering input/state?
2. What earlier decision sent execution here?
3. Would fixing the immediate exception leave the invalid path intact?

Fix the earliest owned rule that explains the symptom without breaking valid cases.
