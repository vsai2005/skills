# Evaluations

The repository keeps three complementary eval layers:

- `activation-cases.json`: machine-readable routing fixtures for whether a primary skill should be selected.
- `behavior-cases.json`: provider-neutral semantic behavior scenarios and expected outcomes.
- `behavior-cases.md`: the same behavior scenarios in a human-friendly form with scoring guidance.
- `live-cases.json`: executable RED/GREEN cases with disposable local fixtures and deterministic graders for all 15 bundled skills.
- `historical-debug-cases.json`: pinned external Git debugging cases based on historical open-source defects; validation is offline, execution intentionally requires network/runtime compatibility.
- `composition-cases.json`: targeted four-arm control/A/B/A+B interaction cases for detecting skill interference or redundant process.

`python scripts/validate_repo.py .` validates JSON syntax, IDs, referenced skill names, negative activation coverage, live fixture/grader schemas, and coverage across all bundled skills.

## Static behavior matrix

Generate a repeated provider-neutral control/treatment plan without calling a model:

```bash
python3 scripts/eval_matrix.py --runs 3 --output .verification/eval-matrix.jsonl
```

This remains useful for teams that have their own harness.

## Executable live behavior suite

Validate fixtures without credentials:

```bash
python3 scripts/live_eval.py validate
python3 scripts/live_eval.py validate --cases evals/historical-debug-cases.json
```

Run real Codex or Claude Code RED/GREEN pairs:

```bash
python3 scripts/live_eval.py run --provider codex --runs 3
python3 scripts/live_eval.py run --provider claude --runs 3 --max-budget-usd 2
```

Then compare paired results:

```bash
python3 scripts/eval_report.py .verification/live-evals/codex-runs.jsonl --fail-on-regression
```

Repository CI validates the definitions and deterministic runner code. It deliberately does **not** spend model tokens or claim live model results. Run important cases through the actual models/harness versions your team uses and retain the generated artifacts.

See [Evaluation Guide](../docs/evaluation.md) and [Live Skill Evaluation Protocol](../docs/live-evaluation.md).


Live cases may declare `expected_change_globs`; the harness uses them only for scope-creep metrics, not as a hard allowlist. Multi-model runs are supported by repeating `--model`, and `eval_report.py` keeps results separated by model.

## Historical debugging cases

The debugging suite can use a `git_fixture` instead of a bundled fixture. A Git fixture pins a credential-free GitHub URL and an exact 40-hex base commit. `validate` checks metadata without network access. `run --dry-run` also avoids cloning; a real run fetches only the pinned commit before applying the same control/treatment skill protocol.

The initial historical cases use SWE-bench Lite metadata for real pytest regressions and our own hidden reproducer scripts. They are kept outside the default local suite because environment compatibility and network access are part of the benchmark rather than repository CI.

## Skill effectiveness and composition

After repeated real live runs, use `scripts/skill_effectiveness.py` to build confidence-qualified provider/model/skill evidence. `scripts/composition_eval.py run` executes control/A/B/A+B interaction matrices instead of only planning them. `scripts/benchmark_campaign.py` coordinates full campaigns and writes strong-only registries only from current, version-matched evidence. These tools are intended to remove unnecessary workflow, not justify loading more skills.

## Empirical campaign policy

`benchmark-policy.json` defines the minimum repeated-pair count, confidence level, bootstrap sample count, minimum score effect, cost threshold, arm-order policy, and core/full suite profiles. Validate it with:

```bash
python3 scripts/benchmark_campaign.py validate
```

Repository CI validates the policy and runner but does not call paid models. See [Empirical Benchmark Campaigns](../docs/empirical-benchmarking.md).
