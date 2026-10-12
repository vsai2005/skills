# Install for Google Antigravity

This repository supports Antigravity 2.0, Antigravity CLI, Antigravity IDE, and the Antigravity SDK through the standard Agent Skills format.

The canonical source remains the repository's `skills/` directory. Do not maintain a second Antigravity-specific copy of the skills.

## Option A: workspace skills

Install all skills into one project:

```bash
python3 scripts/install_skills.py --dest /path/to/project/.agents/skills --all
```

Antigravity uses `.agents/skills/<skill-name>/SKILL.md` for workspace-scoped skills. It also retains backward compatibility with the older `.agent/skills` location, but new installations should use `.agents/skills`.

## Option B: global skills for Antigravity 2.0 or IDE

```bash
python3 scripts/install_skills.py --dest ~/.gemini/config/skills --all
```

These skills are available across workspaces in Antigravity 2.0 and the standalone IDE.

## Option C: global skills for Antigravity CLI

```bash
python3 scripts/install_skills.py --dest ~/.gemini/antigravity-cli/skills --all
```

The CLI exposes installed skills as slash commands such as `/debug-root-cause` and can also select them autonomously from their discovery metadata.

## Option D: generated Antigravity plugin bundle

Antigravity's plugin manifest schema is intentionally strict and is not the same as this repository's portable root `plugin.json`. Do not install the repository root directly as an Antigravity plugin.

Generate an Antigravity-native bundle instead:

```bash
python3 scripts/package_antigravity.py . --output-dir dist
```

This creates:

```text
dist/
├── engineering-quality-antigravity-plugin-v<VERSION>/
│   ├── plugin.json
│   └── skills/
└── engineering-quality-antigravity-plugin-v<VERSION>.zip
```

Install the generated directory with Antigravity CLI:

```bash
agy plugin install ./dist/engineering-quality-antigravity-plugin-v<VERSION>
```

The generated manifest contains only fields accepted by the current Antigravity plugin schema. The skills themselves are copied from the same canonical `skills/` tree used by Codex and Claude Code.

## Option E: Antigravity SDK

The SDK accepts a parent directory containing multiple skill folders:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=["/path/to/cloned/skills-repo/skills"],
)

async with Agent(config) as agent:
    response = await agent.chat("Audit this release end to end.")
    print(await response.text())
```

## Progressive loading and token use

Antigravity indexes skill names and descriptions first and reads full instructions only when a skill is relevant. This repository therefore keeps discovery descriptions compact and enforces a context budget in CI.

The orchestrators also instruct the agent to load only the smallest useful specialist set. Installing all 16 skills does not mean all 16 `SKILL.md` files should be loaded for every task.

## Skill-local helpers and repository utilities

Helpers that a skill explicitly names now travel inside that skill's own `scripts/` directory, so selective installs and the generated Antigravity plugin remain self-contained.

The repository also includes repo-wide validation, benchmarking, packaging, and compatibility commands under the root `scripts/` directory. Clone the repository when you want those development/release utilities.

## Live evaluation

The repository can run Antigravity as a real RED/GREEN provider and can separately benchmark automatic skill selection:

```bash
python3 scripts/live_eval.py run --provider antigravity --model MODEL --runs 3
python3 scripts/activation_eval.py run --provider antigravity --model MODEL --runs 5
```

Real runs are opt-in and require a configured `agy` CLI.

## Verification

After installation, verify both positive and negative activation:

```text
/debug-root-cause Fix this deterministic parser regression without hardcoding the examples.
```

Then ask a normal knowledge question:

```text
Explain JavaScript Array.map to a beginner.
```

The first should use the debugging skill. The second should not require the engineering skill pack.
