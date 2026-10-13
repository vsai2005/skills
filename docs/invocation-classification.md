# Invocation Classification Experiment

Phase 4E separates **model-visible discovery cost** from **human invocation cost** without changing host behavior.

The experiment is defined in:

`evals/invocation-policy.json`

and measured with:

```bash
python3 scripts/invocation_classification.py .
```

## Classification

The policy has three classes.

### model-default

Focused specialists that remain candidates for automatic model selection.

### explicit-candidate

Workflows that may be better as explicit human-invoked commands because they are broad coordinators rather than narrow specialists.

This is an experiment label only. These skills remain discoverable by the model today.

### undecided

Skills with plausible value in both automatic and explicit invocation. Keep current behavior until empirical activation evidence supports a change.

## Current experiment

The initial classification is deliberately conservative:

- explicit-candidate:
  - `engineering-quality`
  - `project-quality-orchestrator`
- undecided:
  - `independent-review`
  - `verify-change`
- model-default:
  - the remaining focused specialists.

The report calculates the discovery metadata that would hypothetically remain if only the explicit candidates were withheld from model-visible discovery.

## Claim boundary

A smaller hypothetical discovery payload is **not** enough to change invocation policy.

Before changing real host behavior, measure:

- activation precision/recall;
- missed useful automatic activation;
- false-positive orchestration;
- task success/quality;
- total tokens, not only discovery tokens;
- human workflow burden;
- provider/model differences.

Do not copy a host-specific field such as an explicit model-invocation disable flag into the provider-neutral `SKILL.md` source unless the repository deliberately adopts a host-specific adapter/policy.

## Why the policy is non-enforced

The policy file contains `"enforced": false`.

The validator rejects turning it on because Phase 4E is a classification experiment, not a silent routing migration. A future invocation change requires its own evidence and explicit implementation.
