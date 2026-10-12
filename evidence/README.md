# Empirical Evidence

This directory is for **published real-model evidence**, not aspirational claims.

The repository already contains deterministic fixtures, graders, paired control/treatment runners, composition experiments, token/cost capture, and statistical qualification. A result belongs in `registry.json` only after a real provider/model campaign has run and the corresponding sanitized aggregate has been reviewed.

## Freshness rules

Published claims are invalidated when:

- the referenced skill content changes, because each claim stores the exact skill-tree SHA-256;
- the evidence becomes older than the registry's `max_age_days`;
- the host/model identity is missing or ambiguous;
- the record no longer has real paired runs.

Run:

```bash
python3 scripts/evidence_freshness.py .
```

CI runs the same check.

## Current status

The registry intentionally starts with **no effectiveness claims** for v1.12.0. CI passing proves repository/test/package integrity; it does not prove that a skill improves every current model.

Use `scripts/benchmark_campaign.py`, `scripts/live_eval.py`, `scripts/activation_eval.py`, `scripts/composition_eval.py`, and `scripts/skill_effectiveness.py` to collect version-bound evidence before publishing a claim.

Publish only strong/current sanitized results:

```bash
python3 scripts/publish_evidence.py \
  /path/to/effectiveness-registry-strong.json \
  --tested-at 2026-10-12T12:00:00Z
```

The publisher refuses unnamed/default models, stale skill hashes, weak evidence, and non-strong classifications.

Do not publish private prompts, credentials, raw proprietary traces, or user data. Publish only sanitized aggregate results needed to support the claim.
