# Changelog

All notable changes to this project will be documented here.

## 1.9.0 - Empirical model evidence and executable composition benchmarks

- Added `benchmark_campaign.py` plus `evals/benchmark-policy.json` for repeatable core/full Codex/Claude benchmark campaigns with explicit models, planned arm counts, campaign manifests, and post-run analysis.
- Live RED/GREEN records now include campaign IDs, exact skill/case/suite hashes, repository version/commit, provider CLI version, and enabled/evaluated skill sets so evidence cannot be silently mixed across changed skills or fixtures.
- RED/GREEN arm order alternates across repetitions to reduce simple time/order bias, and completed arms can be resumed by stable campaign ID without paying to rerun them.
- `skill_effectiveness.py` now uses repeated paired evidence, deterministic bootstrap confidence intervals, exact sign tests, win/pass rates, workflow-cost ratios, and current-skill freshness checks. Strong claims require enough pairs and a confidence interval separated from zero by the configured minimum effect.
- Added `empirical_stats.py` for dependency-free paired statistical helpers.
- `composition_eval.py` can now execute real control/A/B/A+B provider runs with hidden graders, repeated matched comparisons, resume support, and confidence-qualified synergy/interference results instead of only emitting a plan.
- Added a version-controlled empirical benchmark policy and repository/CI validation for it.
- Added focused tests for provenance hashing, alternating arm order, statistical qualification, strong-evidence publication, executable composition matrices, and campaign planning.
- Real Codex/Claude model claims remain opt-in: CI validates the engine and dry-run behavior but does not spend provider tokens or publish fabricated benchmark results.

## 1.8.0 - Adaptive security, self-calibration, and portability

- Added `security-hardening`, a focused trust-boundary/abuse-case workflow for auth/authz, untrusted input, secrets, command/file/network boundaries, value transfer, and supply-chain-sensitive changes.
- Added `skill_effectiveness.py` to build provider/model/skill `BENEFICIAL`/`NEUTRAL`/`COSTLY`/`HARMFUL`/`INSUFFICIENT_DATA` registries from real RED/GREEN results.
- Added targeted `composition-cases.json` plus `composition_eval.py` for control/A/B/A+B skill-interference experiments.
- Added `review_state.py` so independent-review approval is bound to the exact diff and becomes stale after substantive candidate changes.
- Added risk-aware review tiers: no mandatory second reviewer for normal L0/L1 work, one where useful for L2, and two complementary reviewers only for genuinely high-risk L3/L4 boundaries.
- Added FAST/BALANCED/THOROUGH pace as a second axis under L0-L4 risk, plus deterministic retry/review/churn reset signals with `workflow_budget.py`.
- Added a long/noisy-context handoff live case to measure whether current handoff state beats stale historical session material.
- Added runtime-validation guidance to `verify-change` for web/UI, API, CLI, persistence, and async/event boundaries.
- Added `instruction_ablation.py` for controlled pruning experiments instead of permanently accumulating prompt rules.
- Added `portability_check.py`, a Windows Python 3.12 CI lane, pinned current GitHub Actions, and GitHub-Actions-only Dependabot updates.
- Added two security behavior cases, three activation cases, and an executable security RED/GREEN fixture with a hidden ownership-bypass grader.

## 1.7.0 - Debugging depth and historical evaluation

- Strengthened `debug-root-cause` with explicit decision signals, known-good controls, proximate-vs-root-cause checks, runtime-observability guidance, performance profiling/remeasurement, and untrusted/secret-safe diagnostic rules.
- Added four compact debugging references instead of bloating the always-loaded skill body.
- Added rate/confidence-based repetition sizing to `flake_check.py`; a historical failure-rate estimate can now determine N for a desired probability of observing at least one failure.
- Expanded flaky-test guidance to escalate from irrelevant local runs to the failing CI/OS/runtime/parallel environment.
- Added external pinned-Git fixture support to the RED/GREEN live-eval harness. Validation and dry-runs remain offline; real runs fetch the exact commit only when requested.
- Added two historical `debug-root-cause` cases from SWE-bench Lite metadata (`pytest-dev__pytest-11143` and `pytest-dev__pytest-7373`) with independent hidden reproducers.
- Added behavior cases for decision-signal debugging, untrusted diagnostics, profile-first performance debugging, and rate-sized flaky-test reproduction.

## 1.6.0 - 2026-10-08

### Humanizer upgrade

- `humanizer-writing` now audits before rewriting and uses an explicit already-good stop condition so natural text is not rewritten merely to look different.
- Added Light, Standard, and Deep humanization modes so rewrite intensity matches the actual problem.
- Added authentic voice-reference mode based on observable writing features rather than generic "sound human" instructions.
- Added `scripts/humanizer_audit.py` for naturalness signals plus source-vs-rewrite protection checks covering literals, modal language, negation, and suspicious length drift.
- Added `scripts/voice_profile.py` for compact style profiles and candidate comparison without inferring identity or hidden personal traits.
- Added long-form continuity and voice-profile assets plus preservation, genre, and audit-first workflow references.
- Added a second executable RED/GREEN humanizer scenario that measures voice-aware rewriting while protecting version/date/region/performance/compatibility facts.
- Expanded activation and behavior evaluations for voice matching, minimal Light edits, already-good stopping, Deep mode, and long-form continuity.
- Humanization remains a writing-quality workflow: the skill still forbids fake anecdotes, fake personal experience, deliberate errors, false authorship claims, and AI-detector-evasion optimization.

## 1.5.0 - 2026-10-08

### Added

- `humanizer-writing` skill for natural, specific, professional prose that preserves facts, evidence, uncertainty, identifiers, citations, and the author's real point of view.
- Progressive-disclosure naturalness rules, before/after examples, and a reusable humanization review checklist.
- Activation, behavior, and executable RED/GREEN live-eval coverage for the new writing skill, including deterministic checks for factual preservation, reduced formulaic phrasing, varied rhythm, and absence of detector-evasion language.

### Changed

- `engineering-quality`, `AGENTS.md`, README, and usage guidance can route stiff, repetitive, generic, or machine-like prose to `humanizer-writing` without applying it to source code.
- Technical writing can compose `asd-ste100-writing` first for controlled clarity and `humanizer-writing` second for natural rhythm without weakening terminology, warnings, or exact identifiers.
- Context-budget and selective-install expectations now cover 14 bundled skills.

### Integrity note

- The skill improves writing quality rather than attempting to fool AI detectors. It forbids fabricated anecdotes, personal experience, citations, typos, and claims that text is human-authored when that fact is unknown.

## 1.4.0 - 2026-10-08

### Added

- `asd-ste100-writing` skill for clear ASD-STE100-inspired technical prose with a balanced 80% strictness default, stable terminology, short direct sentences, and exact preservation of technical identifiers and constraints.
- Progressive-disclosure writing rules, before/after examples, and a reusable technical-writing review checklist.
- Activation, behavior, and executable RED/GREEN live-eval coverage for the new writing skill, including deterministic checks for preserved UI labels, error codes, timing, warnings, direct procedural language, and prohibited wordy phrases.

### Changed

- `engineering-quality`, `AGENTS.md`, README, and usage guidance can route technical procedures, explanations, release notes, review comments, prompts, and user-facing engineering prose to `asd-ste100-writing` without applying controlled-English rules to code.
- Context-budget and selective-install expectations now cover 13 bundled skills.

### Compliance note

- The skill is deliberately described as **ASD-STE100-inspired**. The repository does not claim certified ASD-STE100 compliance and does not bundle the official controlled vocabulary.

## 1.3.0 - 2026-10-08

### Added

- `context-engineering` skill for minimum-sufficient repository context, local precedent/test discovery, context hygiene, and compact handoffs instead of repository dumps.
- `source-grounded-development` skill for exact-version detection and authoritative-source grounding when framework/SDK/cloud/database behavior is version-sensitive.
- `independent-review` skill for fresh-context review of high-risk/shared changes using consequence × likelihood rather than implementer confidence.
- `scripts/repo_context.py` for deterministic instruction/manifest/version/nearby-test context maps without embedding source contents.
- `scripts/session_handoff.py` for Git-bound long-session handoffs containing goal, scope, decisions, changed files, remaining work, evidence IDs, and pending tests.
- Three new executable live-eval scenarios and hidden graders, bringing live RED/GREEN coverage to all 12 bundled skills.

### Changed

- `engineering-quality` now uses adaptive rigor levels L0-L4 so trivial edits do not inherit migration/security workflow overhead.
- `verify-change` now calls for fresh independent review before the final gate on auth/security, public-contract, migration, architecture, and other high-blast-radius work.
- `context_budget.py` now budgets progressive-disclosure references/assets separately from discovery metadata and core `SKILL.md` text.
- `live_eval.py` accepts repeated `--model` flags, isolates artifacts by model, and records workflow-friction metrics alongside correctness evidence.
- `eval_report.py` groups by provider/model/scenario and reports changed-file count, diff churn, unrelated edits, tool-event signals, duration, tokens, and cost.
- `AGENTS.md` now contains a compact conditional skill router rather than globally forcing every workflow.

### Evaluation philosophy

- Workflow overhead is treated as a measurable cost. A skill should improve reliability without causing unnecessary scope, churn, token use, latency, or tool thrashing.
- Model-specific results remain separate: a skill that helps one model is not assumed to help all models.
- Trace-derived workflow metrics are explicitly best-effort signals; raw provider traces remain the source of truth.

## 1.2.0 - 2026-10-07

### Added

- Executable RED/GREEN live behavioral evaluation with `scripts/live_eval.py` for repeated control/treatment runs through Codex, Claude Code, or a custom command harness.
- `evals/live-cases.json` with one disposable executable scenario for each of the nine bundled skills.
- Provider-independent deterministic graders in `evals/graders/` plus disposable repository fixtures in `evals/live-fixtures/`.
- Raw run artifacts per arm: exact prompt/invocation, stdout/stderr, normalized trace, final response extraction, changed files, grader results, timing, and best-effort token/cost usage.
- `scripts/eval_report.py` for paired control/treatment scoring, pass rates, runtime comparison, treatment-minus-control deltas, and regression classification.
- Claude Code provider-native treatment isolation using a one-skill temporary plugin; control runs disable skills/commands.
- Codex prompt-mounted treatment isolation using a read-only disposable skill copy so the evaluator never modifies the user's global `$CODEX_HOME`.
- `command` provider support for teams that want to wrap another coding-agent harness without adding dependencies to this repository.

### Changed

- Repository validation now validates live-eval schemas, fixture paths, grader definitions, and live coverage for every bundled skill.
- CI validates the live suite without model credentials or model spend.
- Evaluation documentation now distinguishes semantic fixture validation, executable live behavior runs, native activation testing, deterministic grading, and manual semantic review.
- README and manifests updated for v1.2.0 behavioral-evaluation capability.

### Evaluation integrity

- Live model execution remains opt-in and is never claimed by repository CI. The release contains the runner and fixtures, not fabricated Codex/Claude benchmark results.
- Control and treatment use fresh fixture copies and retain inspectable artifacts so an aggregate score cannot hide a bad edit or grader failure.
- Deterministic graders are primary; subjective `manual_checks` remain explicit rather than being silently replaced by an uncalibrated LLM judge.

## 1.1.0 - 2026-10-05

### Added

- `tiered-testing` skill for cheap-versus-heavy verification tiers, early shared-code triggers, and explicit `PENDING_TESTS.md` maintenance.
- `baseline-compare` skill for worktree-first baseline reproduction and per-failure pre-existing/regression classification.
- `flaky-test-triage` skill for N-run failure-rate measurement, order-dependence checks, and shared-resource contention analysis without timeout inflation.
- `baseline_diff.py`, `flake_check.py`, and `pending_tests.py`, each with dependency-free unit coverage.
- `evidence_ledger.py` for timestamped verification command/exit-code evidence and deterministic `Verified` / `Not verified` reporting.
- Activation and behavior eval coverage for all three new skills.

### Hardened after adversarial audit

- Evidence ledger now binds successful local verification to Git HEAD plus a content-sensitive working-tree fingerprint; stale passes move back to `Not verified` after code changes.
- Externally recorded command results are retained as provenance but are no longer presented as locally executed `Verified` evidence.
- `verify-change` now includes outstanding `PENDING_TESTS.md` entries under `Not verified`; pending checks require current executed evidence or an explicit equivalent supersession before removal.
- Release packaging excludes `.verification/` and generated output directories such as `dist/`/`build/`, preventing local evidence or previous release artifacts from leaking/recursing into published ZIPs.
- `flake_check.py` now captures child output (keeping JSON valid), supports per-run timeouts, zero-test output guards, infrastructure exit-code classification, per-run logs, failure-signature grouping, and 95% Wilson intervals.
- `baseline_diff.py` now compares failure identity plus signature, treats same-ID changed signatures conservatively as regressions, rejects null IDs, and accepts JUnit XML inventories.
- Added `context_budget.py` with CI enforcement so discovery metadata/skill bodies cannot grow silently into a token-heavy mega-prompt.
- Added `eval_matrix.py` and a provider-neutral RED/GREEN live-model evaluation protocol for repeated control-versus-skill behavior testing.
- Added an optional isolated mutation-probe protocol for testing whether important new regression tests actually detect the guarded behavior.
- Expanded activation/behavior evals and unit regressions for the audit findings.
- Final release hardening now packages Git-tracked files only when Git is available, rejects symlinks and common secret-bearing filenames, and blocks release while deferred required tests remain.
- Evidence IDs are command-immutable; successful verification that mutates the candidate or cannot be bound to Git state is kept out of `Verified` by default.
- Flake signatures now combine stdout and stderr, known zero-test exit codes can be classified explicitly, and timeout cleanup terminates descendant process groups/trees.
- JUnit baseline identity now uses file/package/suite context when available so same-named tests in different modules remain distinct.
- Completed/superseded pending checks retain a local `.verification/pending_tests_history.jsonl` audit trail.

### Changed

- `verify-change` now builds command-verification reporting from the evidence ledger rather than reconstructing it from memory.
- `engineering-quality` can route testing strategy, baseline attribution, and flaky-test work to the new focused skills.
- README/manifests/version/release metadata updated for nine bundled skills.

## 1.0.1 - 2026-10-05

### Fixed

- `audit_structure.py` now fails on missing/non-directory roots instead of reporting a false clean result.
- `diff_guard.py` now includes untracked working-tree files by default and reports their count.
- Repository validation now executes activation/behavior eval validation, checks `VERSION` against every manifest, validates host skill paths, detects orphaned skill resources, and verifies `FILE_MANIFEST.txt` hashes/sizes.
- Codex and portable manifests now explicitly declare `./skills/`.
- `refactor-safely` now links its migration/contract guidance.
- Skill templates and case studies now live inside the owning skill so selective installation keeps them.
- Activation eval routing coverage now includes direct, indirect, incomplete, ambiguous, trivial, and negative cases; the questionable test-only case no longer forces `verify-change`.
- Behavior evals now cover all six bundled skills and have a machine-readable JSON form.
- Self-audit CI no longer excludes the entire test tree.
- The structure scanner now recognizes more common source extensions, focused/skipped tests, `@ts-expect-error`, `console.debug`, and debugger breakpoints.
- Compatibility docs now point to current OpenAI plugin guidance instead of using the deprecated OpenAI skills repository as the primary reference.
- Release manifests no longer claim an impossible self-size/hash, and checksums use portable archive basenames rather than `/mnt/data` paths.

### Added

- Deterministic `generate_manifest.py` and `package_release.py` release tooling.
- Release/package tests and edge-case regression tests for all audit findings.

## 1.0.0 - 2026-10-05

### Added

- Six focused engineering-quality skills with progressive disclosure.
- Portable OpenAI Agent Plugin, Codex compatibility, and Claude Code plugin manifests.
- Repository/skill validator, heuristic structure auditor, and Git diff scope guard.
- Activation/evaluation cases, templates, examples, CI, contribution guidance, and security policy.
