# Compatibility

This repository targets the common Agent Skills model: each skill lives in a directory with `SKILL.md` and can bundle `references/`, `scripts/`, `assets/`, or examples.

## OpenAI / Codex

The repository includes:

- root `plugin.json` using the portable Agent Plugins manifest shape;
- `.codex-plugin/plugin.json` for Codex plugin discovery;
- `agents/openai.yaml` inside each skill for OpenAI-facing display metadata;
- root-level `skills/`, matching current Codex plugin examples.

For direct skill installation, current Codex tooling also supports user skills under `$CODEX_HOME/skills` (normally `~/.codex/skills`). Plugin discovery is marketplace/local-plugin based and uses `.codex-plugin/plugin.json`.

## Claude Code

The repository includes `.claude-plugin/plugin.json`. Claude Code automatically discovers skill subdirectories under the plugin-root `skills/` directory. Each installed skill remains self-contained because its referenced guidance and reusable assets live inside the skill folder.

Core instructions intentionally avoid requiring Claude-specific commands, so the same source remains useful outside Claude Code.

## Google Antigravity

The canonical `skills/` tree is directly compatible with Antigravity's Agent Skills support. Antigravity 2.0 and the standalone IDE discover workspace skills under `.agents/skills/` and global skills under `~/.gemini/config/skills/`. Antigravity CLI also supports global skills under `~/.gemini/antigravity-cli/skills/`.

Antigravity's plugin manifest schema is stricter than the repository's portable root `plugin.json`, so the root manifest is not presented as an Antigravity plugin manifest. Use `scripts/package_antigravity.py` to generate an Antigravity-native plugin directory and ZIP from the same canonical skill folders.

The Antigravity SDK can point `LocalAgentConfig.skills_paths` directly at this repository's `skills/` parent directory. See [Google Antigravity installation](install-antigravity.md).

## Other harnesses

A compatible harness needs to expose the skill name/description for discovery and make the corresponding `SKILL.md` plus referenced files available when selected. Host-specific UI metadata can be ignored.

## Upstream references

The repository design was rechecked in October 2026 against current public guidance:

- https://developers.openai.com/api/docs/guides/tools-skills
- https://developers.openai.com/plugins/concepts/skills
- https://developers.openai.com/plugins/build/skills
- https://github.com/openai/plugins
- https://github.com/openai/codex
- https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev
- https://github.com/anthropics/claude-plugins-official
- https://antigravity.google/docs/skills
- https://antigravity.google/docs/plugins
- https://antigravity.google/docs/sdk/tools/

Host behavior can evolve. Keep installation documentation versioned and verify platform-specific paths when publishing a release.

## Live evaluation adapters

Core skills remain provider-neutral. Provider-specific behavior is isolated in `scripts/live_eval.py`: Codex runs use current `codex exec --json --full-auto` automation, while Claude Code runs use current non-interactive `-p`/`stream-json` plus a one-skill `--plugin-dir` treatment. These adapters are evaluation tooling, not requirements for using the skills.
