# Workflow Budgets

Risk sets the **minimum safety floor**. Pace controls optional depth above that floor.

## Pace

- **FAST**: smallest evidence that still satisfies the risk level. Skip optional ceremony.
- **BALANCED**: default. Use enough inspection, testing, and review to make the result dependable.
- **THOROUGH**: add broader evidence/review where it can materially reduce uncertainty.

FAST never disables mandatory auth/security/contract/migration checks for L3/L4 work.

## Retry / revision limits

Use these as reset signals, not arbitrary failure caps:

- same failure cause twice without new evidence -> stop patching and rebuild the hypothesis;
- three implementation attempts without a new observation -> return to ownership/contract analysis;
- two review cycles finding the same underlying design problem -> stop local edits and revisit the change contract;
- diff scope or churn grows materially beyond the accepted map -> pause and explain why before continuing.

Do not keep iterating because tool/token budget remains.

## Escalation output

When a budget fires, state:

1. repeated failure/design signal;
2. what evidence is missing;
3. which assumption or contract must be rechecked;
4. the next bounded experiment or redesign decision.

When available, `scripts/workflow_budget.py` can turn attempt/review/churn counts into a deterministic reset signal; thresholds are review prompts, not universal laws.

## Model-specific effectiveness evidence

If a current `skill_effectiveness.py` registry exists for the same provider/model and representative task class, use it to remove optional overhead. A `NEUTRAL`, `COSTLY`, or `HARMFUL` label may justify skipping an optional specialist at L0-L2. It never overrides mandatory security, migration, public-contract, or final-evidence requirements. Treat stale/model-mismatched registries as insufficient data.
