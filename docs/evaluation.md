# Evaluation Guide

A skill can fail in two different ways:

1. **Activation failure**: the right skill is not selected, or the wrong one triggers.
2. **Execution failure**: the correct skill is selected but the workflow produces a poor change.

Test both.

## Activation evaluation

Use `evals/activation-cases.json`. Each case records the expected primary skill or `none`.

Cover multiple forms, not only explicit skill names:

- direct requests;
- indirect wording;
- incomplete but still classifiable requests;
- ambiguous/near-boundary wording;
- mixed-mode work;
- near misses and trivial edits;
- ordinary explanation questions that should not invoke an engineering-change workflow.

When a skill triggers too broadly or too narrowly, improve the frontmatter `description` before adding more body instructions. Discovery happens before the body is loaded.

## Behavior evaluation

Use `evals/behavior-cases.json` for machine-readable scenarios and `evals/behavior-cases.md` for the human scoring form. Run them against disposable repositories/fixtures and score outcomes such as:

- Did the agent inspect existing patterns first?
- Did the bug fix identify a plausible owning rule/root cause?
- Did it avoid hardcoded fixture-specific logic?
- Did a meaningful defect receive regression coverage?
- Were tests/types/lint/security controls preserved?
- Did a refactor keep public behavior/contracts stable?
- Did final reporting distinguish verified from unverified checks?

Repository CI validates eval schema and coverage only. It does **not** claim to execute live model behavior. If your Codex installation includes OpenAI's `plugin-eval` tooling, it can be used as an additional host-specific analysis/benchmark layer; it is optional and not required by this provider-neutral repository.

## Variance

Run important cases more than once and across the models/harnesses the team actually uses. A skill that succeeds only on one lucky run is not reliable enough for a critical workflow.

## Regression evaluation

When changing a skill because of a failure:

1. Add the failing scenario to the eval set.
2. Add at least one nearby scenario that must remain unchanged.
3. Update the smallest instruction/reference that fixes the behavior.
4. Re-run activation and behavior cases.

This is the skill equivalent of adding a regression test before fixing code.
