# Publishing and Distribution

The repository is ready for local/plugin use after validation, but a public marketplace or directory submission can require publisher-specific metadata that this project intentionally does not invent.

## Local and team distribution

For local/team use, keep:

- `.codex-plugin/plugin.json` for Codex plugin packaging;
- `.claude-plugin/plugin.json` for Claude Code plugin packaging;
- root `skills/` for auto-discovered bundled skills;
- root `plugin.json` for portable Agent Plugins-compatible environments.

Run the full repository checks and build a release with `scripts/package_release.py`.

## Public Codex/OpenAI distribution

Before a public submission, review the current OpenAI plugin manifest/submission documentation and add real publisher metadata as required, for example repository/homepage information and any required `interface`/developer/privacy/terms fields. Do not insert placeholder or fabricated URLs merely to satisfy a schema.

Current references:

- https://github.com/openai/plugins
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/build/skills

## Public Claude Code distribution

Before publishing through a Claude plugin marketplace, verify the current marketplace requirements and add real author/repository metadata where needed.

Current reference:

- https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev

## Release integrity

In a Git worktree, releases are built from Git-tracked files only. The release builder rejects symlinks and common secret-bearing filenames rather than following/copying them, and it refuses to package while required `PENDING_TESTS.md` entries remain. Source-archive fallback applies the same symlink/secret policy.

A release should satisfy all of the following:

```bash
python3 scripts/generate_manifest.py .
python3 scripts/validate_repo.py . --warnings-as-errors
python3 scripts/live_eval.py validate
python3 -m unittest discover -s tests -v
python3 scripts/audit_structure.py . \
  --exclude "scripts/audit_structure.py" \
  --exclude "tests/fixtures/audit_structure/**" \
  --fail-on high
python3 scripts/pending_tests.py check
python3 scripts/package_release.py . --output-dir dist
```

The generated `.sha256` file uses the ZIP basename so `sha256sum -c` remains portable after download.
