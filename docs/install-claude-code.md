# Install for Claude Code

The repository is laid out as a Claude Code skill-focused plugin:

```text
engineering-quality-agent-skills/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── structure-feature/
    │   └── SKILL.md
    └── ...
```

Claude Code plugin discovery recognizes the manifest under `.claude-plugin/plugin.json` and auto-discovers skill folders under `skills/` when the plugin is enabled.

## Plugin installation

Install or add this repository through the Claude Code plugin workflow/marketplace mechanism used by your environment, then start a new session so the current skill metadata is available.

## Project-specific use

If a team chooses not to install the whole plugin, copy the desired skill directories into the skill location supported by that project/environment. Preserve each skill directory as a unit; do not copy only `SKILL.md` if it references files under `references/`.

## Recommended division of responsibility

- Put reusable engineering workflow in this plugin.
- Put repository-specific build/test commands and architecture facts in project guidance.
- Avoid duplicating the same rule in several locations unless the host requires it.

## Smoke test

Ask:

```text
Use refactor-safely to split this service while preserving behavior and API contracts.
```

Then inspect whether the agent establishes behavior/contract protection before moving code.
