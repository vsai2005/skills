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

Repository CI validates activation, semantic behavior, and executable live-eval definitions without spending model tokens. `evals/live-cases.json` adds disposable repository fixtures and deterministic graders for every bundled skill. Live Codex/Claude runs remain explicit because they require credentials, sandboxing, and spend limits.

## Variance

Run important cases more than once and across the models/harnesses the team actually uses. A skill that succeeds only on one lucky run is not reliable enough for a critical workflow.

## Regression evaluation

When changing a skill because of a failure:

1. Add the failing scenario to the eval set.
2. Add at least one nearby scenario that must remain unchanged.
3. Update the smallest instruction/reference that fixes the behavior.
4. Re-run activation and behavior cases.

This is the skill equivalent of adding a regression test before fixing code.

## RED/GREEN live-model evaluation

For important skill changes, use the executable A/B protocol in [Live Skill Evaluation Protocol](live-evaluation.md). `scripts/live_eval.py` runs real Codex or Claude Code control/treatment pairs, retains raw traces plus deterministic grading artifacts, alternates arm order across repetitions, and binds results to exact campaign/skill/case hashes. `scripts/eval_matrix.py` remains available for teams with a separate harness.

For publishable empirical evidence, use [Empirical Benchmark Campaigns](empirical-benchmarking.md). A campaign requires repeated paired runs and an explicit model; CI validates the engine but never calls paid models.

## Evaluate workflow cost as well as correctness

v1.3.0+ records workflow-friction signals alongside deterministic correctness: changed-file count, diff churn, unrelated-file count when a scenario declares expected change globs, structured tool-event signals, runtime, tokens and cost. These are comparison signals, not a universal single quality score.

Use repeated `--model` flags to evaluate the same provider/scenarios across multiple models. Reports group results by provider + model + scenario so a skill can be beneficial for one model and neutral or harmful for another.

## Composition and interference

Validate and execute `evals/composition-cases.json` with `scripts/composition_eval.py`. Each repeated case runs control/A-only/B-only/A+B against the same hidden graders so two individually useful skills are not assumed to compose cleanly. Comparisons use matched repetitions and a bootstrap interval for combined-vs-best-single performance.

## Model-specific skill effectiveness

After repeated real RED/GREEN runs, use `scripts/skill_effectiveness.py` to summarize paired score delta, bootstrap confidence interval, exact sign-test evidence, pass rates, and workflow-cost signals by provider + model + skill. Strong claims require enough version-matched pairs; old evidence is stale when the skill hash changes. Treat `PROMISING`, `POSSIBLY_HARMFUL`, and `INSUFFICIENT_DATA` honestly instead of rounding them into a conclusion.

## Instruction ablation

Use `scripts/instruction_ablation.py` to create disposable variants that remove one skill section at a time. Keep sections that measurably help or encode a safety invariant; prune instructions that cost context without changing useful behavior.
