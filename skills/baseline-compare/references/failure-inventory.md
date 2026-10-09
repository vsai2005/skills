# Failure Inventory and Signature Rules

A stable test/check ID is necessary but not always sufficient to prove that a failure is pre-existing.

## Identity + signature

Use both when possible:

```text
failure identity: tests/test_auth.py::test_forbidden
failure signature: expected 403 got 200
```

If the same identity has a materially different signature on the candidate, treat it as a **regression** until equivalence is proved. An old red test can hide a new defect.

## `baseline_diff.py` formats

Text:

```text
id<TAB>signature<TAB>detail
```

The signature/detail columns are optional. With two columns, the second is used as both comparison signature and human detail.

JSON:

```json
[
  {"id": "test.auth", "signature": "expected 403 got 200", "detail": "authorization response mismatch"}
]
```

JUnit XML is also accepted. When available, identity uses `file`/package/suite context before `classname::name`, so two modules with the same class and test name are not collapsed into one failure. Failure/error text is normalized into the comparison signature.

## Missing signature

If both baseline and candidate provide no signature, identity-only matching can be reported as pre-existing with lower evidentiary strength. If only one side has a signature, do not silently assume equivalence; the comparator conservatively treats it as a regression/unproven match.

Prefer stable signatures that exclude volatile timestamps, random IDs, and machine-specific paths.
