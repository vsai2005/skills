# Repository Agent Guidance

This repository publishes reusable Agent Skills. Preserve portability across coding-agent hosts.

## Editing rules

- Keep each `skills/<name>/SKILL.md` focused and compact. Put conditional depth in `references/`.
- Keep reusable templates in the owning skill's `assets/` directory and executable helpers in the owning skill's `scripts/` directory. Skill-relative references must resolve inside that skill so selective installs remain complete.
- Root `scripts/` entry points may wrap skill-local helpers for repository convenience, but the skill-local copy is canonical.
- Keep skill frontmatter to `name` and `description` only unless a target host requires otherwise.
- Use provider-neutral wording in core skill instructions. Product-specific metadata belongs in host-specific manifests or `agents/` metadata.
- Do not add dependencies to the Python utilities unless a dependency materially improves reliability.
- Treat thresholds in scanners as heuristics, not universal engineering laws.
- Add or update tests when changing scripts, metadata rules, eval schemas, or repository validation behavior.
- Keep `VERSION` and all plugin manifest versions aligned.

## Conditional skill router

Use the smallest applicable workflow:

- unfamiliar/large repository or stale/noisy context -> `context-engineering`;
- version-sensitive framework/SDK/cloud/database behavior -> `source-grounded-development`;
- shared/public contract or architecture boundary -> `guard-architecture`;
- intermittent test -> `flaky-test-triage`; already-red baseline -> `baseline-compare`;
- auth/authz/secrets/untrusted command-file-network/value boundary -> `security-hardening`;
- high-risk completed change -> `independent-review` before `verify-change`;
- technical docs/procedures/explanations that need controlled, consistent English -> `asd-ste100-writing`;
- prose that is accurate but stiff, repetitive, generic, machine-like, or needs authentic voice matching -> `humanizer-writing`;
- broad source-to-consumer audit, repeated systemic defect, release/freeze readiness -> `project-quality-orchestrator`;
- final readiness -> `verify-change`.

Do not invoke extra skills for a trivial local edit merely because they exist.

## Verification policy

Run the **smallest check set that can falsify the changed requirement**, then broaden when risk or evidence requires it. Do not run the complete repository gate after every local edit.

Use these defaults:

- **Docs/Markdown only:** validate the affected content and run repository/manifest checks only when the changed files participate in those contracts.
- **Skill description or metadata:** run repository validation, OpenAI metadata freshness, context budget, and activation validation.
- **Skill body/reference/asset:** run repository validation, context budget, and the affected deterministic tests/evals. Broaden when routing, shared schemas, or several skills changed.
- **Python helper/script:** compile the changed module and run its targeted unit tests. Run the full unit suite when shared test/eval infrastructure or common helpers changed.
- **Eval schema/runner:** validate the affected eval family and run targeted tests. Broaden to all eval validators when common eval infrastructure changed.
- **Security, public contracts, packaging, release, or broad orchestration changes:** escalate verification according to blast radius and use the appropriate specialist skill.

A failed focused check, a shared-code edit, or an unexpected side effect is a reason to broaden verification. A green focused check is not proof of a consumer layer that was never exercised.

### Output discipline

Keep successful verification output concise so logs do not become model context.

- Prefer quiet/default test output for green runs.
- For the full Python unit suite, use `python3 -m unittest discover -s tests`. If it fails, rerun the failing module/test with `-v` for diagnosis.
- Preserve failing test IDs, relevant tracebacks, and command exit status.
- Do not feed complete green logs back into the model when a summary is enough.
- When a tool can write a large log/artifact to disk, keep the full evidence there and return a compact summary plus the path.
- Do not truncate evidence needed to diagnose a failure.

## Pull request and release gate

Pull-request CI remains the comprehensive deterministic backstop across supported Python/OS lanes. A local task does not need to duplicate the whole CI matrix unless CI is unavailable or the failure is being reproduced locally.

Before merge/release, require the relevant CI checks to pass. For release work, also run or confirm:

```bash
python3 scripts/pending_tests.py check
python3 scripts/package_antigravity.py . --output-dir dist
python3 scripts/export_standard_evals.py . --output-dir dist/standard-evals
python3 scripts/package_release.py . --output-dir dist
unzip -t dist/engineering-quality-agent-skills-v$(cat VERSION).zip
```

Do not weaken checks just to make CI pass. Fix the underlying issue or document a justified exception. If a required check is intentionally delegated to PR CI, report that explicitly instead of claiming it was run locally.
