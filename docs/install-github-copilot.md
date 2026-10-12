# Install for GitHub Copilot

GitHub documents Agent Skills as an open-standard customization supported by Copilot in VS Code, Copilot CLI, and Copilot coding-agent surfaces.

Supported project locations include:

```text
.github/skills/<skill-name>/
.claude/skills/<skill-name>/
.agents/skills/<skill-name>/
```

Supported personal locations include:

```text
~/.copilot/skills/<skill-name>/
~/.agents/skills/<skill-name>/
```

## Project install

Install all skills into a repository-local Copilot location:

```bash
python3 scripts/install_skills.py --dest /path/to/project/.github/skills --all
```

Or use the cross-agent project location:

```bash
python3 scripts/install_skills.py --dest /path/to/project/.agents/skills --all
```

## Personal install

```bash
python3 scripts/install_skills.py --dest ~/.copilot/skills --all
```

## Verification status

The skill structure is documented-compatible with GitHub Copilot, but this repository does not yet publish native Copilot activation or behavior benchmark results. See [Host support matrix](host-support.md).

Do not interpret structural compatibility as proof that every Copilot model/version selects every skill correctly. Use the same activation and RED/GREEN evaluation discipline before promoting Copilot to empirically verified status.
