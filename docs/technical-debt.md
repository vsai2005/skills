# Deliberate Technical Debt

The skills distinguish **accidental patch-stack debt** from **deliberate bounded debt**.

A workaround is acceptable only when its tradeoff is explicit and the safer/full solution is genuinely unavailable or outside the current safe scope. Use the record in `skills/engineering-quality/references/technical-debt.md`.

The most important field is the **removal condition**. A calendar date can be useful, but an engineering condition is often stronger:

- minimum supported provider SDK reaches a fixed version;
- old consumers finish migration;
- feature flag rollout reaches 100%;
- upstream issue is confirmed resolved;
- data backfill completes and verification passes.

Without a removal condition, a "temporary" branch tends to become permanent architecture.
