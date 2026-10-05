# Install for OpenAI / Codex

## Option A: install as a Codex plugin

The Codex plugin manifest is `.codex-plugin/plugin.json`, with bundled skills under the root `skills/` directory. Current Codex plugin discovery is marketplace/local-plugin based. Add this plugin directory to the marketplace/local-plugin mechanism supported by your Codex environment, then enable the plugin.

The root `plugin.json` is also retained for portable Agent Plugins-compatible environments.

## Option B: install selected user skills

Current Codex skill tooling uses `$CODEX_HOME/skills` (normally `~/.codex/skills`) for user-installed skills. You can copy only the workflows you want:

```bash
python3 scripts/install_skills.py --dest ~/.codex/skills debug-root-cause verify-change
```

The installer copies the full skill directory, including `references/`, `assets/`, and `agents/` metadata.

## Option C: repository-local harness directory

If your Codex/harness configuration explicitly scans a repository-local skill directory, point the included installer at that directory. Do not assume a repo-local path is supported unless your client/harness documents it.

## Recommended project guidance

Keep project-specific facts in the project's `AGENTS.md`: commands, architecture facts, generated directories, local naming conventions, deployment constraints, and files that must not be edited.

Keep reusable behavior in the skills. This prevents a global quality skill from accumulating one project's special cases.

## Verification

After installing, try one direct and one negative activation case:

```text
Use debug-root-cause to fix this failing parser regression.
```

```text
Explain JavaScript Array.map to a beginner.
```

The first should use the debugging workflow. The second should not need this engineering-change skill pack.
