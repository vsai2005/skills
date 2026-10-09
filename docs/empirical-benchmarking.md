# Empirical Benchmark Campaigns

The repository can plan and run repeated real-model campaigns instead of treating one RED/GREEN pair as proof.

## Why this exists

Model behavior is stochastic and provider/model behavior changes over time. A skill should not be called beneficial because one treatment run happened to succeed. Empirical claims must be tied to:

- the exact provider and explicit model;
- the exact skill bytes;
- the exact benchmark case definition;
- the provider CLI version;
- the repository version/commit;
- repeated paired control/treatment runs;
- inspectable artifacts and deterministic graders.

## Validate the campaign policy

```bash
python3 scripts/benchmark_campaign.py validate
```

The default policy requires at least five paired repetitions for a claim and uses a deterministic 95% bootstrap interval over paired score deltas.

## Plan before spending model tokens

```bash
python3 scripts/benchmark_campaign.py plan \
  --provider codex \
  --model MODEL \
  --profile full \
  --runs 5
```

Profiles:

- `core`: all local RED/GREEN cases;
- `full`: local cases + historical debugging cases + composition/interference cases.

A one-model `full` campaign currently plans hundreds of isolated arms. Review the plan before execution.

## Run a real Codex campaign

```bash
python3 scripts/benchmark_campaign.py run \
  --provider codex \
  --model MODEL \
  --profile full \
  --runs 5 \
  --output-dir .verification/benchmarks/codex-MODEL
```

## Run a real Claude Code campaign

```bash
python3 scripts/benchmark_campaign.py run \
  --provider claude \
  --model MODEL \
  --profile full \
  --runs 5 \
  --max-budget-usd 2.00 \
  --output-dir .verification/benchmarks/claude-MODEL
```

Real campaigns require an explicit `--model`; evidence from an unnamed provider default is deliberately not treated as publishable model-specific evidence.

## Resume an interrupted campaign

Use the same campaign identifier:

```bash
python3 scripts/benchmark_campaign.py run \
  --provider codex \
  --model MODEL \
  --profile full \
  --runs 5 \
  --campaign-id empirical-... \
  --resume \
  --output-dir .verification/benchmarks/codex-MODEL
```

Completed local/historical arms are skipped rather than billed again. Composition runs also preserve campaign identity and support resume.

## Bias control

Normal RED/GREEN repetitions alternate execution order:

```text
run 1: control -> treatment
run 2: treatment -> control
run 3: control -> treatment
...
```

This does not remove provider drift, but it reduces simple time/order bias.

## What is recorded

Each arm records:

- campaign ID;
- provider and provider CLI version;
- explicit model;
- skill hash(es);
- case hash and suite hash;
- repository version and Git commit;
- platform/Python metadata;
- exact invocation and prompt;
- raw stdout/stderr and normalized trace;
- final workspace/diff;
- deterministic grader results;
- score/pass state;
- duration, best-effort token/cost usage, and workflow-friction metrics.

Do not merge records whose skill/case versions differ and call them one experiment.

## Statistical evidence

`skill_effectiveness.py` pairs exact control/treatment attempts and reports:

- mean and median paired score delta;
- deterministic bootstrap confidence interval;
- exact sign-test p-value;
- treatment win rate;
- pass-rate change;
- token/time ratios;
- churn and unrelated-file signals.

Example:

```bash
python3 scripts/skill_effectiveness.py \
  .verification/benchmarks/codex-MODEL/local/codex-runs.jsonl \
  .verification/benchmarks/codex-MODEL/historical/codex-runs.jsonl \
  --repo . \
  --min-pairs 5 \
  --markdown \
  --output .verification/benchmarks/codex-MODEL/effectiveness.md
```

A `BENEFICIAL` or `HARMFUL` strong claim requires the minimum number of pairs and a confidence interval separated from zero by the configured minimum effect. Smaller/uncertain effects are reported as `PROMISING`, `POSSIBLY_HARMFUL`, `NEUTRAL`, `COSTLY`, or `INSUFFICIENT_DATA` instead of being overstated.

Evidence is marked stale when the current skill hash no longer matches the benchmarked skill.

## Composition/interference evidence

Composition cases can now be executed, not only planned:

```bash
python3 scripts/composition_eval.py run \
  --provider codex \
  --model MODEL \
  --runs 5 \
  --output-dir .verification/composition
```

Each case runs:

1. control;
2. skill A only;
3. skill B only;
4. A+B combined.

The comparison uses repeated matched runs and a bootstrap interval for `combined - best(single)`. The result is `SYNERGY`, `NEUTRAL_OR_REDUNDANT`, `INTERFERENCE`, or `INCONCLUSIVE`.

## Publication rule

The campaign automatically writes both:

- `effectiveness-registry.json`: all evidence, including uncertain evidence;
- `effectiveness-registry-strong.json`: only strong, current evidence.

Do not hand-edit those files into stronger claims. Re-run the campaign when the model, skill, benchmark, or provider interface changes.

## What this release does not claim

Repository CI validates the campaign engine, schemas, statistics, resume behavior, and dry-run plans. It does **not** call paid external models. Real Codex/Claude evidence exists only after a user runs a campaign with those provider CLIs installed and retains the generated artifacts.
