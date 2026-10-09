# Worktree Baseline

Prefer a detached worktree so the candidate checkout remains untouched.

Example:

```bash
git worktree add --detach ../baseline-worktree <baseline-ref>
```

Then run the same preparation and verification command in both trees.

## Comparison discipline

- keep runtime/dependency versions equivalent when possible;
- use the same test selection and flags;
- reset/seed external state equivalently;
- capture failure identities, not only totals;
- remove the worktree when finished.

Example cleanup:

```bash
git worktree remove ../baseline-worktree
```

If a worktree cannot be used, state why before switching to a manual reconstruction.

## Failure inventory format

When using `scripts/baseline_diff.py`, provide either JSON lists or newline-delimited text. Text records use a stable failure ID followed by an optional tab-separated detail:

```text
tests/test_auth.py::test_forbidden	returned 200 instead of 403
tests/test_export.py::test_empty_export
```

Use the same identity rule for baseline and candidate; do not compare only aggregate failure counts.
