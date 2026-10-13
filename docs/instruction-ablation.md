# Token-aware instruction ablation

Use `scripts/instruction_ablation.py` to test whether one skill section is still
earning its context cost. The tool creates an isolated copy for experiments and
compares experiment records. It never edits the source skill.

## Create an ablated variant

```bash
python3 scripts/instruction_ablation.py create   skills/example-skill   --section "Optional process detail"   --output-dir .verification/ablation/example-without-section
```

Run the full and ablated variants against the same cases, provider/model,
repository state, and repetition policy. Alternate arm order when the harness
supports it.

## Record format

The comparator accepts JSONL rows with `variant` equal to `control`, `full`,
or `ablated`. Completed rows should use the same fields emitted by the live
benchmark harness when available:

```json
{
  "variant": "full",
  "status": "completed",
  "score_fraction": 1.0,
  "passed": true,
  "duration_seconds": 12.3,
  "usage": {
    "input_tokens": 12000,
    "output_tokens": 1800,
    "cached_input_tokens": 5000
  },
  "workflow_metrics": {
    "tool_event_count": 9
  }
}
```

A row can set `"protected_instruction": true` when the tested section is a
mandatory safety or contract rule.

## Compare

```bash
python3 scripts/instruction_ablation.py compare records.jsonl
```

Default policy:

- score may fall by at most 0.01;
- total input + output token use must drop by at least 2%;
- duration or tool-event count must not regress by more than 10%;
- protected instructions never become prune candidates.

Possible decisions:

- `PRUNE_CANDIDATE`: quality is non-inferior, real token data exists, token
  savings are material, no measured cost signal regressed materially, and the
  instruction is not protected.
- `KEEP_SECTION`: quality regressed.
- `PROTECTED_KEEP`: the instruction is safety/contract protected.
- `INSUFFICIENT_TOKEN_DATA`: quality can be compared but token savings cannot.
- `NO_MATERIAL_TOKEN_SAVINGS`: the section did not earn enough context savings
  to justify removal.
- `COST_REGRESSION_KEEP`: token use fell but another measured workflow cost
  regressed materially.
- `INSUFFICIENT_DATA`: full/ablated quality evidence is missing.

## Interpretation

`PRUNE_CANDIDATE` is not an automatic edit. Review the section's purpose,
activation boundary, safety/contract role, and experiment provenance before
changing the source skill.

Do not use a one-off synthetic record to make an effectiveness claim. Real
model behavior is stochastic; use repeated matched provider runs when deciding
whether an instruction can be removed without quality loss.

Do not ablate authentication, authorization, secrets, destructive-action
boundaries, evidence honesty, or other mandatory safety/contract rules merely
to reduce tokens.
