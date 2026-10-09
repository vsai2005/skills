# Adaptive Rigor

Use the smallest process that matches semantic risk. Line count alone is not risk.

| Level | Typical change | Default process |
| --- | --- | --- |
| L0 — trivial | typo, local rename, obvious mechanical edit | edit + smallest relevant check |
| L1 — focused | ordinary local bug or small feature | one specialist skill + targeted verification |
| L2 — shared | shared utility, provider adapter, common validator, multi-caller behavior | specialist + broader callers/tests + scope review |
| L3 — high-risk | auth/security, persistence migration, public API/event, architecture boundary | change contract + context/source grounding as needed + specialist + independent review + full verification |
| L4 — long-horizon | multi-phase feature/refactor/migration across sessions | staged checkpoints + context map + handoff state + independent review + final evidence gate |

## Escalation signals

Escalate when the change affects security, money/data loss, public contracts, persisted data, independent deployments, many callers, concurrency, external providers, or unclear repository ownership.

## De-escalation rule

Do not invoke planning/review/test ceremony merely because the skills exist. If a task becomes simpler after inspection, use the lower level.

## Pace is a second axis

After choosing L0-L4, choose FAST/BALANCED/THOROUGH from [workflow-budgets.md](workflow-budgets.md). Pace can remove optional work, but it cannot lower the minimum safety floor of the risk level.
