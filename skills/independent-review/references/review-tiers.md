# Review Tiers

Use semantic risk, not line count.

- **L0/L1**: no mandatory independent reviewer unless requested or a specific risk appears.
- **L2**: one fresh reviewer when the change is shared, unfamiliar, or difficult to verify locally.
- **L3/L4**: one independent review is required before final verification. For security, persistence, money/value transfer, public contracts, migrations, or architecture-wide changes, use **two complementary reviewers** when the host can isolate them efficiently.

Complementary reviewers should not duplicate the same checklist. Example split:

- reviewer A: correctness, contracts, data/state, architecture;
- reviewer B: security/failure paths, test integrity, runtime/operational risk.

A review is evidence about a specific diff. If substantive code changes after the review, treat affected review conclusions as stale and re-review the changed surface.

## Bind review evidence to the diff

When `scripts/review_state.py` is available, record a completed review against the exact candidate diff:

```bash
python3 scripts/review_state.py record --id REVIEW-001 --base <base-ref> --outcome approved .
python3 scripts/review_state.py check --id REVIEW-001 .
```

Any substantive diff change makes the conservative fingerprint stale. Re-review the affected surface rather than carrying an old approval forward.
