# Bug-Fix Anti-Patterns

## Fixture-specific hardcoding

Bad signal:

```text
if value == "Go": ...
if value == "C": ...
if value == "R": ...
```

when the real defect is a language/technology classifier that confuses reserved short names with ordinary tokens.

Correct direction: repair the classifier's taxonomy/boundary and test several representative positive and negative cases.

## Error swallowing

Returning a safe-looking default after catching every exception can convert visible failure into silent data corruption. Catch only where there is a defined recovery or translation policy.

## Timeout inflation

Increasing a timeout can be correct for a changed latency requirement, but is suspicious when used to hide nondeterminism, a deadlock, or a race.

## Mocking away the failure

If the defect occurs in a repository/provider integration, replacing that layer with a mock may make the test green without testing the defect.

## Test weakening

Suspicious changes include deleting the failing case, replacing exact assertions with `is not None`, skipping it, or asserting only that no exception occurs when the output matters.

## Compatibility branch multiplication

Repeated `if oldVersion`, `if legacy`, `if specialProvider` branches across modules often indicate missing adapter ownership. Centralize compatibility at a boundary when semantics allow it.
