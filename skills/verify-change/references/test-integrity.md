# Test Integrity

Green tests are useful only when the tests still represent the contract.

## Suspicious changes

- exact output assertion becomes only truthy/non-null;
- failing edge case is removed from a parameterized set;
- test is skipped/xfail without a documented external reason;
- integration test becomes a unit test with the failing boundary mocked;
- timeout/sleep increases without latency requirement change;
- expected exception becomes `try/except: pass`;
- production code checks a test environment variable to bypass behavior.

## Legitimate test changes

Tests should change when:

- requirements intentionally changed;
- the old test asserted implementation detail rather than contract;
- a flaky test had an invalid synchronization assumption and is replaced with deterministic observation;
- a fixture was objectively invalid/unrepresentative.

State the reason when a meaningful assertion is relaxed or removed.
