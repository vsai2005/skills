# Contributing

Contributions should improve reliability without turning the skills into giant universal prompts.

## Principles

1. Prefer a small rule that changes decisions over generic advice the model already knows.
2. Keep triggering descriptions precise. A good skill should activate for the right tasks and stay out of unrelated work.
3. Put mode-specific details in references so they are loaded only when needed.
4. Keep reusable templates/case material inside the skill that needs it so selective installs remain self-contained.
5. Add representative activation and behavior cases for skill behavior changes.
6. Keep deterministic scripts conservative and clearly label heuristics.

## Development

Requirements: Python 3.10+ and Git for `diff_guard.py` integration checks.

```bash
python3 -m compileall -q scripts tests
python3 scripts/generate_manifest.py .
python3 scripts/validate_repo.py . --warnings-as-errors
python3 scripts/context_budget.py . --fail-on-budget
python3 scripts/live_eval.py validate
python3 -m unittest discover -s tests -v
python3 scripts/audit_structure.py . \
  --exclude "scripts/audit_structure.py" \
  --exclude "tests/fixtures/audit_structure/**" \
  --fail-on high
```

The manifest must be regenerated after repository files change because validation checks file size and SHA-256 integrity.

## Release smoke test

```bash
python3 scripts/pending_tests.py check
python3 scripts/package_release.py . --output-dir dist
unzip -t dist/engineering-quality-agent-skills-v$(cat VERSION).zip
```

`package_release.py` writes a deterministic ZIP and a portable `.sha256` file that contains only the archive filename, not a machine-specific absolute path.

## Pull-request checklist

- Skill metadata still matches its purpose and trigger conditions.
- New local Markdown links resolve and bundled skill resources are reachable from `SKILL.md`.
- Scripts have tests for changed behavior, including important failure paths.
- Activation and behavior eval fixtures cover the changed routing/workflow behavior.
- No provider-specific instruction leaked into provider-neutral core skills without a reason.
- No check or test was weakened solely to get a green build.
- `FILE_MANIFEST.txt` was regenerated after the final edits.

## Behavioral evaluation

For skill-behavior changes, add/adjust activation and behavior fixtures and use the RED/GREEN protocol in [docs/live-evaluation.md](docs/live-evaluation.md) when validating against a real agent harness.
