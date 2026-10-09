# Skill Composition Evaluation

Skills can be useful alone and harmful when stacked. `evals/composition-cases.json` defines targeted two-skill interaction cases and reuses hidden graders from the corresponding live fixture.

Validate and inspect the four-arm matrix:

```bash
python3 scripts/composition_eval.py validate
python3 scripts/composition_eval.py plan --provider codex --model MODEL --runs 5
```

Each repeated case contains:

1. control;
2. skill A only;
3. skill B only;
4. A+B combined.

## Execute real provider runs

```bash
python3 scripts/composition_eval.py run \
  --provider codex \
  --model MODEL \
  --runs 5 \
  --output-dir .verification/composition-evals
```

Claude Code and the custom command provider are supported too. `--case` selects a focused interaction. A stable `--campaign-id --resume` avoids repeating completed arms after interruption.

## Compare completed arms

```bash
python3 scripts/composition_eval.py compare \
  .verification/composition-evals/codex-composition-runs.jsonl \
  --min-runs 5 \
  --fail-on-interference
```

The comparison uses matched repetitions and a bootstrap confidence interval for `combined - best(single)`. Results are `SYNERGY`, `NEUTRAL_OR_REDUNDANT`, `INTERFERENCE`, or `INCONCLUSIVE`.

A combined arm should not be preferred merely because it contains more process. Compare correctness and workflow cost together.
