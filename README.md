# Engineering Quality Agent Skills

A portable, provider-neutral skill pack for AI coding agents that helps keep software clean **while building features, fixing bugs, refactoring, reviewing architecture, planning tests, selecting context, grounding changing APIs, reviewing high-risk work, hardening trust boundaries, writing clear and natural prose, triaging failures, measuring skill effectiveness, and verifying changes**.

The goal is simple: a change should not be considered successful merely because the tests are green. It should solve the right problem without making the codebase harder to understand, maintain, test, secure, or extend.

## Why this exists

AI coding agents are very good at producing working code quickly. Repeated changes can still accumulate technical debt when an agent:

- adds another conditional instead of correcting the underlying model or abstraction;
- hardcodes one failing example instead of fixing the general rule;
- duplicates logic that already exists elsewhere;
- grows a component, service, route, or utility file until it owns too many responsibilities;
- changes broad areas of the repository for a narrow bug;
- weakens tests, types, validation, or lint rules to obtain a green build;
- leaves temporary debug code, dead code, disabled checks, or compatibility hacks behind;
- performs a large refactor without locking current behavior first.

This repository packages a repeatable engineering workflow around those failure modes.

## The skill set

| Skill | Use it for | Core outcome |
| --- | --- | --- |
| `engineering-quality` | Multi-mode or end-to-end engineering work | Select the smallest useful workflow and coordinate quality gates |
| `structure-feature` | Building or extending software | Put new code in the right place with clear responsibilities |
| `debug-root-cause` | Reproducible bugs, regressions, failing tests | Reproduce, form testable hypotheses, use safe runtime evidence, and fix the owning cause instead of the symptom |
| `refactor-safely` | Cleanup, decomposition, modernization | Improve structure while preserving behavior and contracts |
| `guard-architecture` | Architecture-sensitive changes and reviews | Protect dependency direction, ownership, boundaries, and blast radius |
| `tiered-testing` | Cheap/heavy verification planning | Run fast checks continuously and defer heavy checks explicitly |
| `baseline-compare` | Already-red or noisy test suites | Classify every current failure as pre-existing or regression |
| `flaky-test-triage` | Intermittent/nondeterministic tests | Measure failure rate and isolate order/contention causes |
| `verify-change` | Pre-merge/final verification | Prove the change works from recorded verification evidence |
| `context-engineering` | Unfamiliar/large/noisy repository context | Load the smallest useful local context instead of dumping the repo |
| `source-grounded-development` | Version-sensitive external APIs/frameworks | Ground decisions in the exact local version and authoritative sources |
| `independent-review` | High-risk/fresh-context second review | Catch self-review blind spots before final verification |
| `security-hardening` | Auth, secrets, untrusted input, command/file/network/value boundaries | Trace trust boundaries, test abuse cases, and repair the owning security control |
| `asd-ste100-writing` | Technical procedures, explanations, release notes, reviews, and user-facing engineering prose | Write clear ASD-STE100-inspired controlled English while preserving exact technical meaning |
| `humanizer-writing` | Prose that is correct but stiff, repetitive, generic, or machine-like | Make writing natural, specific, and professional without inventing facts or a fake author voice |

The skills are intentionally separate. Loading every rule for every task creates noisy context and can make agents less effective. v1.9.0 uses adaptive rigor (L0-L4) plus FAST/BALANCED/THOROUGH pace so a trivial edit does not inherit the workflow cost of a migration or security change. Detailed material is stored under each skill's `references/` directory and should be read only when the task needs it.


### Debugging depth and self-calibrating workflow

`debug-root-cause` now separates the proximate failure from the owning cause, asks for a prediction/decision signal before non-trivial experiments, and provides selective references for runtime observability, performance profiling, and secret-safe diagnostics. `flaky-test-triage` can size the repetition count from an estimated historical failure rate and desired detection confidence.

The live-eval system also supports pinned external Git fixtures. `evals/historical-debug-cases.json` starts with two real pytest regressions from SWE-bench Lite metadata; their hidden reproducers are separate from the model prompt. Normal repository CI validates these cases without network access, while intentional live runs fetch the exact historical base commit.

v1.9.0 adds version-bound empirical benchmark campaigns on top of the v1.8.0 self-calibration work. Repeated control/treatment runs now carry exact skill/case hashes, campaign identity, provider/model provenance, balanced arm ordering, resumable execution, bootstrap confidence intervals, and executable four-arm composition tests. The goal is to remove workflow that no longer helps stronger models instead of accumulating process forever.

## What makes this different from a style guide

This pack is about **decision quality**, not tabs versus spaces.

It gives an agent process-level guardrails such as:

- inspect the repository before inventing a new pattern;
- define intended scope before editing;
- choose the smallest correct fix, not the smallest diff at any cost;
- establish a root-cause hypothesis for bug fixes, with an explicit decision signal and known-good control when useful;
- treat logs, stack traces, issue text, and remote error bodies as untrusted evidence and keep diagnostics secret-safe;
- measure/profile performance regressions before optimizing and remeasure the same workload afterward;
- distinguish behavior-preserving refactors from behavior changes;
- protect public contracts, stored data, auth boundaries, and shared APIs;
- add regression coverage for meaningful defects;
- keep tests honest;
- review failure paths, security-sensitive paths, and obvious performance risks;
- check the final diff for architecture drift, dead code, and temporary bypasses.

## Operating model

```text
Request
  |
  v
Classify the change
  |-- new capability ----------> structure-feature
  |-- bug/regression ----------> debug-root-cause
  |-- cleanup/modernization ---> refactor-safely
  |-- boundary-sensitive ------> guard-architecture
  |-- cheap/heavy test plan ----> tiered-testing
  |-- baseline attribution -----> baseline-compare
  |-- intermittent test --------> flaky-test-triage
  |-- context uncertainty ------> context-engineering
  |-- changing external API ---> source-grounded-development
  |-- security/trust boundary --> security-hardening
  |-- high-risk second review --> independent-review
  |-- controlled technical prose -> asd-ste100-writing
  |-- natural prose rewrite ------> humanizer-writing
  |-- ready-to-merge check ----> verify-change
  `-- spans several modes -----> engineering-quality
                                      |
                                      v
                               verify-change gate
```

A specialized skill should be preferred when one clearly matches the task. `engineering-quality` exists for work that genuinely spans modes; it is not intended to load the whole pack for every edit.

## Quick start

### Use as an OpenAI/Codex plugin

The repository includes a portable `plugin.json` plus `.codex-plugin/plugin.json` compatibility metadata. The `skills/` directory follows the current Agent Skills structure. Codex plugin discovery uses the plugin manifest/marketplace flow, while direct user skill installs normally live under `$CODEX_HOME/skills` (commonly `~/.codex/skills`). See [OpenAI/Codex installation](docs/install-openai-codex.md).

### Use with Claude Code

The repository also includes `.claude-plugin/plugin.json`. Claude Code plugins auto-discover skill folders under `skills/` when the plugin is installed/enabled. See [Claude Code installation](docs/install-claude-code.md).

### Use with another Agent Skills compatible harness

Expose one or more folders under `skills/` as Agent Skills. Each skill has standard `SKILL.md` metadata and keeps host-specific UI configuration outside its core instructions.

### Copy skills into any explicit skill directory

The included installer is intentionally harness-neutral:

```bash
python3 scripts/install_skills.py --dest /path/to/skills --all
python3 scripts/install_skills.py --dest /path/to/skills debug-root-cause verify-change
```

It refuses to overwrite existing skill folders unless `--force` is supplied. See [Using the skills effectively](docs/using-the-skills.md) for invocation and project-guidance patterns.

## Example requests

```text
Build an account settings feature in this existing Next.js repo. Use the
structure-feature skill and preserve the repository's existing conventions.
```

```text
Fix this parser regression. Use debug-root-cause. Do not hardcode the failing
fixtures; find the classification rule that is actually wrong and add a
regression test.
```

```text
This component is 1,300 lines. Use refactor-safely to split responsibilities
without changing behavior, routes, public props, or persisted state.
```

```text
Review this patch with verify-change. Check tests, type/lint bypasses,
error paths, architecture drift, dead code, and whether the tests were weakened.
```

```text
Our suite is already red. Use baseline-compare to prove which failures existed
before this patch and which are regressions.
```

```text
This test passes on rerun. Use flaky-test-triage, run it 20 times, report the
failure rate, and investigate order/shared-resource causes without timeout bumps.
```

```text
Use security-hardening on this ownership update. Trace the authorization boundary,
test a cross-user abuse case, preserve legitimate owner/admin behavior, and do not
log secrets while debugging.
```

```text
Rewrite this troubleshooting procedure with asd-ste100-writing. Use about 80%
strictness, keep exact UI/API identifiers unchanged, and do not claim certified
ASD-STE100 compliance.
```

```text
Humanize this engineering update with humanizer-writing. Keep every factual claim,
number, identifier, and source intact; remove templated filler and repetitive rhythm.
```


### Controlled technical writing

`asd-ste100-writing` uses practical controlled-English principles inspired by ASD-STE100. Its default is about 80% strictness so technical text stays clear without becoming mechanical. It preserves exact identifiers, UI labels, commands, numbers, warnings, and contract terms. The repository does **not** claim that using the skill produces certified ASD-STE100-compliant text, and it does not bundle the official controlled vocabulary.

### Natural human-sounding writing

`humanizer-writing` now uses an audit-first workflow with Light, Standard, and Deep intensity. It can build a compact voice profile from authentic writing samples, stop when a draft is already natural, preserve protected literals and modal/negation strength, and maintain a continuity ledger for long documents. It deliberately does **not** add fake typos, anecdotes, personal experience, or claims of human authorship, and it does not optimize for AI-detector evasion. When technical controlled English is also required, apply `asd-ste100-writing` first and humanize lightly afterward.

## Included deterministic utilities

The skills are instruction-first. The repository also ships optional local helpers:

### Validate the skill repository

```bash
python3 scripts/validate_repo.py .
```

Checks skill names/frontmatter, host metadata, manifest/version consistency, activation/semantic/live eval schemas and fixtures, local Markdown links, progressive-disclosure resource reachability, and the release file manifest.

### Heuristic structure audit

```bash
python3 scripts/audit_structure.py /path/to/project
python3 scripts/audit_structure.py /path/to/project --json
python3 scripts/audit_structure.py /path/to/project --fail-on high
```

Looks for signals such as very large source files, skipped tests, type/lint suppression, empty catches, and debug leftovers. It is deliberately heuristic; a finding is a review prompt, not proof of a defect.

### Diff scope guard

```bash
python3 scripts/diff_guard.py /path/to/repo --base HEAD~1
```

Summarizes tracked **and untracked** working-tree files, churn, concentration, and broad-scope signals so a narrow task that unexpectedly touches many areas gets another look. Commit-to-commit comparisons intentionally ignore unrelated working-tree files.

### Baseline failure comparison

```bash
python3 scripts/baseline_diff.py baseline-failures.txt current-failures.txt --fail-on-regression
```

Classifies every current failure as `pre-existing` or `regression`, compares failure signatures so an old red test cannot hide a new failure mode, accepts text/JSON/JUnit XML inventories, disambiguates JUnit identities with file/package/suite metadata when available, and reports baseline failures that disappeared.

### Flake repetition check

```bash
python3 scripts/flake_check.py --runs 20 --timeout 120 --zero-tests-exit-code 5 --log-dir .verification/flake-example -- python -m pytest tests/test_example.py -q
```

Runs the exact command N times with captured output, optional per-run timeout/zero-test guard/infrastructure classification, grouped failure signatures, and a 95% sampling interval. Order-dependence and contention experiments remain deliberate triage steps rather than hidden timeout changes.

### Deferred heavy-test queue

```bash
python3 scripts/pending_tests.py add \
  --command "npm run e2e" \
  --reason "browser environment unavailable" \
  --trigger "before merge"
```

Maintains a machine-readable `PENDING_TESTS.md` so required heavy checks are not forgotten. Completion requires current ledger-executed evidence or an explicit equivalent supersession, writes a local completion history, and blocks release packaging while required pending checks remain.

### Verification evidence ledger

```bash
ID=$(python3 scripts/evidence_ledger.py plan --label "Unit tests" --command "python -m unittest discover -s tests -v")
python3 scripts/evidence_ledger.py run --id "$ID" --label "Unit tests" -- python -m unittest discover -s tests -v
python3 scripts/evidence_ledger.py report
```

Records verification commands with timestamps, provenance, Git HEAD, and a content-sensitive repository fingerprint. Evidence IDs are command-bound; passing evidence becomes stale after code changes; successful commands that mutate the candidate or cannot be bound to Git state are not normal `Verified` evidence; externally recorded results remain provenance only; and outstanding `PENDING_TESTS.md` entries appear under `Not verified`.

### Empirical model benchmarking

```bash
python3 scripts/benchmark_campaign.py plan --provider codex --model MODEL --profile full --runs 5
python3 scripts/benchmark_campaign.py run --provider codex --model MODEL --profile full --runs 5
```

Campaigns repeat real control/treatment runs, alternate arm order, bind evidence to exact skill/case hashes, retain provider/model/CLI provenance, and generate confidence-qualified effectiveness registries. Real runs require the provider CLI and an explicit model; repository CI never fabricates model evidence. See [Empirical Benchmark Campaigns](docs/empirical-benchmarking.md).

### Model-specific skill effectiveness

```bash
python3 scripts/skill_effectiveness.py \
  .verification/benchmarks/local/codex-runs.jsonl \
  --repo . --min-pairs 5 --markdown
```

Reports paired deltas, bootstrap confidence intervals, sign-test evidence, pass rates, and token/time/churn signals. Strong `BENEFICIAL`/`HARMFUL` claims require repeated version-matched evidence; uncertain results stay `PROMISING`, `POSSIBLY_HARMFUL`, `NEUTRAL`, `COSTLY`, or `INSUFFICIENT_DATA`. See [Skill Effectiveness and Pruning](docs/skill-effectiveness.md).

### Skill-composition interference

```bash
python3 scripts/composition_eval.py validate
python3 scripts/composition_eval.py run --provider codex --model MODEL --runs 5
python3 scripts/composition_eval.py compare .verification/composition-evals/codex-composition-runs.jsonl --fail-on-interference
```

Executes and compares control/A-only/B-only/A+B experiments for targeted skill combinations rather than assuming stacked skills help. See [Skill Composition Evaluation](docs/composition-evaluation.md).

### State-bound independent review

```bash
python3 scripts/review_state.py record --id REVIEW-001 --base HEAD^ --outcome approved .
python3 scripts/review_state.py check --id REVIEW-001 .
```

Binds an independent-review result to the exact diff fingerprint so substantive edits make old review evidence stale.

### Workflow retry/churn budget

```bash
python3 scripts/workflow_budget.py --level L2 --attempts 3 --same-failure 2 --files 9 --churn 700
```

Turns repeated-failure/review/scope signals into a reset recommendation instead of letting agents patch indefinitely. Thresholds are heuristics, not universal laws.

### Instruction ablation

```bash
python3 scripts/instruction_ablation.py create skills/debug-root-cause --section "Separate symptom from cause" --output-dir /tmp/debug-ablated
```

Creates disposable section-ablated skill variants for controlled evaluation. Do not prune a safety invariant merely because a weak benchmark fails to exercise it.

### Cross-host portability smoke check

```bash
python3 scripts/portability_check.py . --warnings-as-errors
```

Checks portable manifests, minimal core frontmatter, host-neutral skill bodies, and obvious path issues. See [Cross-host Portability](docs/portability.md).

### Context-budget check

```bash
python3 scripts/context_budget.py . --fail-on-budget
```

Guards the total discovery metadata and individual skill size so the pack does not become a token-heavy mega-framework. See [Context Budget](docs/context-budget.md).

### Repository context map

```bash
python3 scripts/repo_context.py . --target src/accounts
```

Produces a compact map of applicable instructions, manifests/versions, likely commands, nearby source/tests, and current changes without embedding repository contents.

### Session handoff

```bash
python3 scripts/session_handoff.py . --goal "Finish account migration" --remaining "Run e2e"
```

Creates a concise Git-bound handoff with goal, scope, decisions, changed files, pending work, evidence IDs, and pending tests for long tasks or new sessions.

### Humanizer naturalness audit

```bash
python3 scripts/humanizer_audit.py audit DRAFT.md
python3 scripts/humanizer_audit.py compare DRAFT.md HUMANIZED.md --fail-on-warning
```

Reports heuristic naturalness signals before rewriting and deterministic preservation risks afterward. The comparison checks protected literals, modal/negation drift, and suspicious length changes. It is a writing-quality helper, not an authorship or detector classifier.

### Voice-profile helper

```bash
python3 scripts/voice_profile.py VOICE_SAMPLE.md
python3 scripts/voice_profile.py VOICE_SAMPLE.md --candidate HUMANIZED.md
```

Builds a compact profile from observable features such as sentence rhythm, paragraph density, contractions, point-of-view markers, punctuation, transition frequency, and vocabulary density. It does not infer identity, demographics, personality, or other hidden traits.

### RED/GREEN behavior evaluation

Validate the executable live suite without credentials:

```bash
python3 scripts/live_eval.py validate
```

Run repeated control/treatment pairs through real Codex or Claude Code:

```bash
python3 scripts/live_eval.py run --provider codex --runs 3
python3 scripts/live_eval.py run --provider claude --runs 3 --max-budget-usd 2
```

Then compare paired deterministic scores:

```bash
python3 scripts/eval_report.py .verification/live-evals/codex-runs.jsonl --fail-on-regression
```

The bundled `evals/live-cases.json` suite covers every skill and adds focused extra scenarios where needed, with disposable fixtures, hidden deterministic graders, raw trace retention, changed-file evidence, timing, and best-effort token/cost extraction. Codex treatment runs use a prompt-mounted read-only skill copy so the evaluator never mutates the user's global `$CODEX_HOME`; Claude treatment runs use an isolated native plugin with `--plugin-dir`, while control runs disable skills. See [Live Skill Evaluation Protocol](docs/live-evaluation.md).

For teams with their own harness, `scripts/eval_matrix.py` still emits a provider-neutral JSONL control/treatment plan.

### Generate and verify the release manifest

```bash
python3 scripts/generate_manifest.py .
python3 scripts/generate_manifest.py . --check
```

`FILE_MANIFEST.txt` stores SHA-256 and byte size for every release file except the manifest itself and transient VCS/cache files.

### Build a deterministic release

```bash
python3 scripts/package_release.py . --output-dir dist
```

Creates `engineering-quality-agent-skills-v<version>.zip` plus a portable `.sha256` file whose checksum line uses only the archive filename. In a Git worktree the release uses tracked files only; source-archive fallback rejects symlinks and obvious credential filenames. Packaging also refuses to proceed while `PENDING_TESTS.md` still contains required checks.

## Quality philosophy

The pack follows five rules:

1. **Correctness before cosmetics.** Formatting cannot compensate for a wrong design or root cause.
2. **Repository fit before personal preference.** Follow good existing conventions unless there is a concrete reason to change them.
3. **Minimal correct change before minimal line count.** A two-line workaround can be worse than a fifteen-line root-cause fix.
4. **Evidence before confidence.** Reproduce bugs, run relevant checks, and distinguish what was verified from what was inferred.
5. **Maintainability is part of done.** A patch that works today but increases hidden coupling or disables safeguards is incomplete.

## Soft complexity budgets

The repository includes complexity guidance, but intentionally avoids universal hard line limits. A generated parser, migration, schema snapshot, or test fixture can legitimately be large. A 700-line React component mixing data fetching, validation, state machines, and presentation is different.

The question is not only "how many lines?" but:

- how many reasons does this unit have to change?
- can its behavior be tested without unrelated setup?
- does it cross architectural layers?
- is duplicated logic emerging?
- can a developer find the owner of a rule quickly?
- did this task make the next change easier or harder?

## Repository layout

```text
engineering-quality-agent-skills/
├── plugin.json                  # Portable Agent Plugin manifest
├── .codex-plugin/plugin.json   # Codex compatibility manifest
├── .claude-plugin/plugin.json  # Claude Code plugin manifest
├── skills/
│   ├── engineering-quality/    # SKILL.md + references + reusable assets
│   ├── structure-feature/      # Includes worked feature-structure case study
│   ├── debug-root-cause/       # Includes bug-fix record + root-cause case study
│   ├── refactor-safely/        # Includes refactor plan + migration guidance
│   ├── guard-architecture/     # Includes architecture-review template
│   ├── tiered-testing/         # Cheap/heavy tiers + pending-test policy
│   ├── baseline-compare/       # Worktree baseline + comparison report
│   ├── flaky-test-triage/      # Repetition/order/contention triage
│   ├── verify-change/          # Evidence-led completion report
│   ├── context-engineering/    # Minimum-sufficient repository context
│   ├── source-grounded-development/ # Exact-version external grounding
│   ├── independent-review/     # Fresh, state-bound review
│   ├── security-hardening/     # Trust boundaries + abuse-case verification
│   ├── asd-ste100-writing/     # Controlled technical English
│   └── humanizer-writing/      # Natural, fact-preserving prose
├── scripts/                    # Validation, release, evidence, eval, portability helpers
├── tests/                      # Utility/metadata/release/eval regression tests
├── evals/                      # Activation, semantic behavior, live fixtures + graders
├── examples/project-guidance/ # Example repository-specific AGENTS.md
└── docs/                       # Installation, design, customization, eval guidance
```

## Design sources

The structure follows current Agent Skills conventions: a skill is a folder with `SKILL.md`, with optional `references/`, `scripts/`, and assets. The descriptions are written to carry activation intent, while the bodies remain focused and use progressive disclosure. Provider-specific presentation metadata is kept separate from the core workflow.

See [Design principles](docs/design-principles.md), [Compatibility](docs/compatibility.md), [Context Budget](docs/context-budget.md), [Skill Effectiveness](docs/skill-effectiveness.md), [Composition Evaluation](docs/composition-evaluation.md), [Portability](docs/portability.md), and [Live Skill Evaluation Protocol](docs/live-evaluation.md) for the rationale and evaluation model used by this repository. See [Publishing and distribution](docs/publishing.md) before preparing a public marketplace/directory submission.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Good contributions usually add one of:

- a reproducible failure mode the current rules miss;
- a clearer decision rule;
- a better activation/evaluation case;
- a conservative deterministic check with low false-positive cost;
- a reference that helps only when its mode is active.

Avoid adding generic "write clean code" prose that does not change an agent's decisions.

## License

MIT. See [LICENSE](LICENSE).
