# Engineering Quality Agent Skills

A portable, provider-neutral skill pack for AI coding agents that helps keep software clean **while building features, fixing bugs, refactoring, reviewing architecture, and verifying changes**.

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
| `debug-root-cause` | Bugs, regressions, flaky behavior, failing tests | Reproduce, isolate, explain, and fix the cause instead of the symptom |
| `refactor-safely` | Cleanup, decomposition, modernization | Improve structure while preserving behavior and contracts |
| `guard-architecture` | Architecture-sensitive changes and reviews | Protect dependency direction, ownership, boundaries, and blast radius |
| `verify-change` | Pre-merge/final verification | Prove the change works without weakened checks or hidden debt |

The skills are intentionally separate. Loading every rule for every task creates noisy context and can make agents less effective. Detailed material is stored under each skill's `references/` directory and should be read only when the task needs it.

## What makes this different from a style guide

This pack is about **decision quality**, not tabs versus spaces.

It gives an agent process-level guardrails such as:

- inspect the repository before inventing a new pattern;
- define intended scope before editing;
- choose the smallest correct fix, not the smallest diff at any cost;
- establish a root-cause hypothesis for bug fixes;
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

## Included deterministic utilities

The skills are instruction-first. The repository also ships optional local helpers:

### Validate the skill repository

```bash
python3 scripts/validate_repo.py .
```

Checks skill names/frontmatter, host metadata, manifest/version consistency, activation and behavior eval schemas, local Markdown links, progressive-disclosure resource reachability, and the release file manifest.

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

Creates `engineering-quality-agent-skills-v<version>.zip` plus a portable `.sha256` file whose checksum line uses only the archive filename.

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
│   └── verify-change/          # Includes completion report + integrity case study
├── scripts/                    # Validation, audit, diff, install, release helpers
├── tests/                      # Utility/metadata/release regression tests
├── evals/                      # Activation + machine-readable behavior cases
├── examples/project-guidance/ # Example repository-specific AGENTS.md
└── docs/                       # Installation, design, customization, eval guidance
```

## Design sources

The structure follows current Agent Skills conventions: a skill is a folder with `SKILL.md`, with optional `references/`, `scripts/`, and assets. The descriptions are written to carry activation intent, while the bodies remain focused and use progressive disclosure. Provider-specific presentation metadata is kept separate from the core workflow.

See [Design principles](docs/design-principles.md) and [Compatibility](docs/compatibility.md) for the rationale and official references used when building this repository. See [Publishing and distribution](docs/publishing.md) before preparing a public marketplace/directory submission.

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
