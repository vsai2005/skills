# Live Skill Evaluation Protocol

v1.9.0 adds version-bound campaign provenance, alternating control/treatment order, resumable repeated runs, confidence-qualified effectiveness evidence, and executable composition experiments. Historical debugging cases remain separate from the default local suite.

Static validation proves that skill files, metadata, scripts, fixtures, and release artifacts are internally consistent. It does **not** prove that a coding model follows a skill reliably. v1.2.0 introduced an executable RED/GREEN harness for that second problem; v1.3.0 added model-separated runs and workflow-friction evidence so quality gains can be weighed against scope, churn, latency, tokens, and cost.

## What the harness measures

For every live scenario, run the same repository fixture and user request in two isolated arms:

```text
same fixture + same request
        |
        +-- control / RED ------ skill unavailable
        |
        `-- treatment / GREEN -- target skill available
                                  |
                                  v
                         deterministic graders
                                  |
                                  v
                          paired comparison
```

Repeat the pair several times. Model behavior is stochastic, so one successful treatment run is not sufficient evidence.

The bundled live suite in `evals/live-cases.json` covers every bundled skill and includes additional focused scenarios where one case is not enough (for example long-context handoff and voice matching). Fixtures live under `evals/live-fixtures/`; hidden deterministic graders live under `evals/graders/`.

## Validate the live suite without model credentials

```bash
python3 scripts/live_eval.py validate
```

This checks case IDs, skill names, fixture paths, setup commands, grader schemas, thresholds, and full bundled-skill coverage. Repository CI runs this validation but does not spend model tokens.

To inspect planned Codex invocations without calling Codex:

```bash
python3 scripts/live_eval.py run \
  --provider codex \
  --runs 1 \
  --dry-run \
  --output-dir .verification/live-evals-plan
```

## Run with Codex

Current OpenAI guidance recommends `codex exec --json` for automated skill evals so the harness can retain structured JSONL events and grade actual tool/file behavior. The runner uses `--full-auto` for fixture workspaces.

```bash
python3 scripts/live_eval.py run \
  --provider codex \
  --runs 3 \
  --output-dir .verification/live-evals
```

Optionally choose a model:

```bash
python3 scripts/live_eval.py run \
  --provider codex \
  --model <model> \
  --runs 3
```

### Codex skill-loading isolation

The runner does **not** modify the user's global `$CODEX_HOME`. For treatment runs it mounts a read-only copy of the target skill inside the disposable fixture and adds a short instruction to read that exact `SKILL.md`. Control runs receive only the original task.

This measures whether the skill instructions improve behavior while avoiding global-install side effects. It does **not** claim to measure Codex's native automatic skill-discovery/activation rate. Use `evals/activation-cases.json` or a separately prepared disposable Codex installation when native activation itself is the property under test.

## Run with Claude Code

Claude Code supports non-interactive `-p`, `stream-json`, per-session plugin loading, and a flag that disables skills/commands for a control run. The runner therefore uses provider-native skill loading for the Claude treatment arm:

```bash
python3 scripts/live_eval.py run \
  --provider claude \
  --runs 3 \
  --max-budget-usd 2.00 \
  --output-dir .verification/live-evals
```

Treatment runs build an isolated temporary plugin containing only the target skill and load it with `--plugin-dir`. Control runs use `--disable-slash-commands`.

A user's other Claude configuration may still affect a session. For high-stakes benchmarking, run in a dedicated account/config/environment and record the Claude Code version/model with the artifacts.

## Run another harness

The `command` provider lets a team wrap another coding agent or a test double without adding a dependency here. Pass an argv array as JSON. `{prompt}`, `{workspace}`, and `{run_dir}` are substituted literally; no shell is inserted automatically.

```bash
python3 scripts/live_eval.py run \
  --provider command \
  --runs 2 \
  --command-json '["my-agent","--cwd","{workspace}","--prompt","{prompt}"]'
```

## Select scenarios

Run all bundled local cases by default, or repeat `--case` for a targeted subset:

```bash
python3 scripts/live_eval.py run \
  --provider codex \
  --runs 5 \
  --case debug-root-cause-classifier-live \
  --case verify-test-integrity-live
```

## Artifacts retained per arm

Each arm gets a fresh fixture copy and its own artifact directory containing:

- `prompt.txt` — exact prompt passed to the provider;
- `invocation.json` — argv and skill-loading strategy;
- `stdout.log` / `stderr.log` — raw provider output;
- `trace.txt` — searchable normalized trace text;
- `final.txt` — best-effort extracted final response;
- `changed-files.json` — Git-visible repository changes;
- `result.json` — provider status, timing, usage, graders, and score;
- the complete final fixture workspace.

Run records are also appended to `<output-dir>/<provider>-runs.jsonl`.

## Deterministic graders first

Live cases use objective graders where possible:

- post-run commands/hidden tests;
- required or forbidden file content;
- regular expressions over provider traces;
- changed-file bounds;
- file-size/line-count review signals.

The runner records `manual_checks` separately for semantic questions that should not be faked as deterministic. Examples include whether a root-cause explanation is actually supported or whether an extraction has a coherent responsibility.

Do not add an LLM judge merely because prose is hard to score. If a model judge is later added, calibrate it against human labels before treating its score as authoritative.

## Compare control and treatment

After live runs:

```bash
python3 scripts/eval_report.py \
  .verification/live-evals/codex-runs.jsonl \
  --output .verification/live-evals/codex-report.md \
  --fail-on-regression
```

The report calculates:

- control and treatment mean deterministic score;
- paired treatment-minus-control delta;
- control/treatment pass rates;
- mean runtime;
- classification: `improved`, `neutral-good`, `regressed`, `no-material-improvement`, or `inconclusive`.

A skill does not need a positive delta when the control is already excellent. A treatment that remains excellent without material regression is `neutral-good`. A treatment that performs worse is a regression even if its prose sounds more disciplined.

## Token/cost evidence

Provider JSONL schemas evolve. The runner therefore records raw output and performs best-effort extraction of common usage fields such as `input_tokens`, `output_tokens`, cache-token fields, duration, and cost when present. Treat raw provider traces as the source of truth.

A skill should justify its context/latency cost with more reliable behavior. Compare quality and overhead together.

## Safety and budget rules

Live evals execute coding agents against disposable repositories. They can run commands and edit files.

- Use only disposable fixtures/workspaces.
- Do not point the harness at a production repository.
- Keep provider credentials outside fixtures and generated artifacts.
- Use provider budget/turn controls where available.
- Inspect raw traces before sharing them publicly; they may contain environment details.
- Keep live model runs out of public contribution CI unless credentials, sandboxing, and spend limits are deliberately configured.

## Current provider references

The runner's defaults were checked against current public documentation:

- OpenAI skill evals with `codex exec --json --full-auto`: https://developers.openai.com/blog/eval-skills
- OpenAI skills guidance: https://developers.openai.com/plugins/build/skills
- Claude Code CLI reference (`-p`, `stream-json`, `--plugin-dir`, `--disable-slash-commands`): https://code.claude.com/docs/en/cli-reference
- Claude Code plugin skill structure/testing: https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev

Provider CLIs evolve. Keep adapters small, version the observed provider binary in every run record, and update tests/docs when an upstream interface changes.

## Model matrix

Run the same cases across multiple models by repeating `--model`:

```bash
python3 scripts/live_eval.py run --provider codex --model MODEL_A --model MODEL_B --runs 3
```

The report groups provider/model/scenario independently. Do not assume a workflow that helps one model helps every model.

## Workflow-friction metrics

Each completed arm writes `workflow-metrics.json` containing deterministic scope/churn measures plus best-effort trace signals. Current fields include changed-file count, diff churn, unrelated-file count (when the case declares expected change globs), tool-event count, repeated read signals, clarification signals, prompt size and final-response size. Combine these with runtime/token/cost evidence when deciding whether a skill's quality gain justifies its overhead. Raw traces remain authoritative when provider event schemas change.

## External historical Git fixtures

A live case may use `git_fixture` instead of a bundled `fixture`:

```json
{
  "git_fixture": {
    "repo_url": "https://github.com/owner/repo.git",
    "base_commit": "40-hex pinned commit"
  }
}
```

Validation is offline and requires a credential-free GitHub HTTPS URL plus an exact commit. Dry-runs do not fetch the repository. A real run initializes an empty workspace, fetches only the pinned commit, checks it out detached, then applies the normal control/treatment and hidden-grader flow. Keep environment/runtime requirements explicit because historical projects may not run on current interpreters.

`evals/historical-debug-cases.json` is deliberately separate from the default local suite so CI remains deterministic and network-free.

## Effectiveness and composition follow-up

After live runs, `scripts/skill_effectiveness.py` can build provider/model/skill evidence labels. `scripts/composition_eval.py` plans four-arm interaction tests so stacked skills are evaluated rather than assumed to help. See `docs/skill-effectiveness.md` and `docs/composition-evaluation.md`.

## v1.9 empirical campaign provenance

Every new run record carries a campaign ID, skill hash(es), case hash, suite hash, repository version/commit, provider CLI version, explicit model, and runtime metadata. Use a stable `--campaign-id --resume` to continue interrupted paid runs.

By default repeated arms alternate order (`control -> treatment`, then `treatment -> control`) to reduce simple time/order bias. Use `scripts/benchmark_campaign.py` for full repeated campaigns and `scripts/skill_effectiveness.py` for confidence-qualified evidence. See [Empirical Benchmark Campaigns](empirical-benchmarking.md).
