# Repository Agent Guidance

This repository publishes reusable Agent Skills. Preserve portability across coding-agent hosts.

## Editing rules

- Keep each `skills/<name>/SKILL.md` focused and compact. Put conditional depth in `references/`.
- Keep reusable templates in the owning skill's `assets/` directory and link them from `SKILL.md` so selective installs remain complete.
- Keep skill frontmatter to `name` and `description` only unless a target host requires otherwise.
- Use provider-neutral wording in core skill instructions. Product-specific metadata belongs in host-specific manifests or `agents/` metadata.
- Do not add dependencies to the Python utilities unless a dependency materially improves reliability.
- Treat thresholds in scanners as heuristics, not universal engineering laws.
- Add or update tests when changing scripts, metadata rules, eval schemas, or repository validation behavior.
- Keep `VERSION` and all plugin manifest versions aligned.

## Required checks

Run before finishing changes:

```bash
python3 -m compileall -q scripts tests
python3 scripts/generate_manifest.py .
python3 scripts/validate_repo.py . --warnings-as-errors
python3 -m unittest discover -s tests -v
python3 scripts/audit_structure.py . \
  --exclude "scripts/audit_structure.py" \
  --exclude "tests/fixtures/audit_structure/**" \
  --fail-on high
```

For release work, also run:

```bash
python3 scripts/package_release.py . --output-dir dist
unzip -t dist/engineering-quality-agent-skills-v$(cat VERSION).zip
```

Do not weaken checks just to make CI pass. Fix the underlying issue or document a justified exception.
