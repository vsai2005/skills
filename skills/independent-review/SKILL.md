---
name: independent-review
description: Perform a fresh-context review of a meaningful software change after implementation, especially for shared/high-blast-radius code, authentication/security, public contracts, migrations, large refactors, architecture changes, or explicit review requests. Use to reduce self-review blind spots by judging the final diff against the original request, repository constraints, and verification evidence without relying on the implementer's reasoning narrative.
---

# Independent Review

Review the **final change**, not the implementer's confidence or internal reasoning.

## 1. Decide whether independent review is warranted

Use it for high-impact/shared changes, auth/security, persistence migrations, public APIs/events, architecture changes, large refactors, or when the user explicitly requests a second review.

Use [references/review-tiers.md](references/review-tiers.md): L0/L1 normally needs no independent reviewer; L2 may use one; L3/L4 requires fresh review, with two complementary reviewers only for genuinely high-risk boundaries when the host can isolate them efficiently.

Do not force a separate review for trivial L0/L1 edits unless risk justifies it.

## 2. Build fresh review context

Give the reviewer only what is needed:

- original request and accepted scope;
- applicable repository guidance;
- final diff;
- relevant architecture/contracts;
- tests/evidence actually run;
- known remaining risks.

Do **not** rely on the implementer's step-by-step reasoning or intended conclusions.

## 3. Review by consequence and likelihood

Inspect correctness, security, data/contract compatibility, architecture, test integrity, maintainability and obvious performance impact.

Classify findings using [references/severity-likelihood.md](references/severity-likelihood.md), not theoretical severity alone.

## 4. Prefer actionable findings

Every finding should identify:

```text
location
violated contract/invariant
consequence
likelihood/evidence
smallest correct repair
```

Avoid style commentary unless it materially affects maintainability or repository conventions.

## 5. Resolve before final verification

The implementer should address or explicitly disposition important findings, then rerun relevant verification. Treat the review as bound to the reviewed diff; if substantive behavior changes afterward, re-review the affected surface. When available, use `scripts/review_state.py` as described in [references/review-tiers.md](references/review-tiers.md) so stale review approval is detected mechanically. `verify-change` remains the final evidence gate.

For substantial reviews use [assets/review-report.md](assets/review-report.md) and [references/review-scope.md](references/review-scope.md).
