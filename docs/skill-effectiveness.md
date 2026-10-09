# Skill Effectiveness and Pruning

A skill is not permanently useful because it once helped an older model. Measure paired control/treatment behavior on the exact models and task classes you use.

## Strong evidence

After repeated real runs:

```bash
python3 scripts/skill_effectiveness.py \
  .verification/benchmarks/local/codex-runs.jsonl \
  --repo . \
  --min-pairs 5 \
  --markdown \
  --output .verification/skill-effectiveness.md
```

The registry reports mean/median paired score delta, a deterministic bootstrap confidence interval, exact sign-test p-value, win/pass rates, token/time ratios, churn, and unrelated-file signals.

Strong `BENEFICIAL` or `HARMFUL` claims require enough paired repetitions and a confidence interval separated from zero by the configured minimum effect. Smaller/uncertain effects remain `PROMISING`, `POSSIBLY_HARMFUL`, `NEUTRAL`, `COSTLY`, or `INSUFFICIENT_DATA`.

Evidence records carry exact skill/case hashes. With `--repo .`, evidence becomes `stale` when the current skill bytes differ from the benchmarked version.

Use `--strong-only` only for publishing a conservative registry; keep the full registry for audit.

## Routing rule

Use effectiveness evidence to remove **optional** workflow overhead. Never use a benchmark label to skip a mandatory security, migration, public-contract, or evidence requirement for the current task.

## Prune instructions, not only whole skills

Use `scripts/instruction_ablation.py` to compare a full skill against a section-ablated variant. Retain a section when it measurably helps or encodes a non-negotiable safety invariant.

See [Empirical Benchmark Campaigns](empirical-benchmarking.md) for repeated real-model execution.
