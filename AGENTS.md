# Repository Agent Guidance

This repo publishes reusable Agent Skills. Preserve portability across coding-agent hosts.

## Editing rules

- Keep `skills/<name>/SKILL.md` compact; put conditional depth in `references/`.
- Keep templates/assets/scripts with their owning skill so selective installs remain complete.
- Root `scripts/` may wrap skill-local helpers; the skill-local copy is canonical.
- Keep frontmatter to `name` and `description` unless a host requires more.
- Keep core skill wording provider-neutral; host metadata belongs in manifests or `agents/`.
- Add dependencies only when they materially improve reliability.
- Treat scanner thresholds as heuristics.
- Update tests for changed scripts, metadata rules, eval schemas, or validation behavior.
- Keep `VERSION` and plugin manifest versions aligned.

## Conditional skill router

Use the smallest applicable workflow:

- unfamiliar/large repo or stale context -> `context-engineering`;
- version-sensitive external behavior -> `source-grounded-development`;
- shared/public contract or architecture boundary -> `guard-architecture`;
- intermittent test -> `flaky-test-triage`; already-red baseline -> `baseline-compare`;
- auth/secrets/untrusted command-file-network/value boundary -> `security-hardening`;
- high-risk completed change -> `independent-review` before `verify-change`;
- controlled technical prose -> `asd-ste100-writing`;
- stiff/generic but accurate prose -> `humanizer-writing`;
- broad source-to-consumer audit, systemic defect, release/freeze readiness -> `project-quality-orchestrator`;
- final readiness -> `verify-change`.

Do not add skills to a trivial task merely because they exist.

## Verification policy

Run the **smallest checks that can falsify the changed requirement**. Broaden after a failed focused check, shared/high-risk edit, or unexpected side effect.

- docs -> affected content; repo/manifest only if those contracts changed;
- skill metadata/description -> repo validation + metadata freshness + context budget + activation validation;
- skill body/reference/asset -> repo validation + context budget + affected tests/evals;
- Python helper -> compile + targeted tests; full suite for shared helpers/infrastructure;
- eval infrastructure -> affected eval validation + targeted tests; broaden for common schemas/runners;
- security/public contract/packaging/release/broad orchestration -> escalate by blast radius.

Do not run the full repository gate after every local edit. PR CI is the comprehensive deterministic backstop across supported OS/Python lanes.

### Output discipline

Keep green output concise:
- full suite: `python3 -m unittest discover -s tests`;
- on failure, rerun the failing test/module with `-v`;
- preserve failing IDs, relevant traceback, exit status, and the full-log/artifact path;
- do not feed complete green logs to the model when a summary is enough.

## Release gate

Before merge/release, require relevant PR CI to pass. For release work, also run or confirm:

```bash
python3 scripts/pending_tests.py check
python3 scripts/package_antigravity.py . --output-dir dist
python3 scripts/export_standard_evals.py . --output-dir dist/standard-evals
python3 scripts/package_release.py . --output-dir dist
unzip -t dist/engineering-quality-agent-skills-v$(cat VERSION).zip
```

Do not weaken checks to make CI pass. If a required check is delegated to PR CI, say so instead of claiming it ran locally.
