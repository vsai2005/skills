# Host support matrix

"Supports Agent Skills" can mean several different things. This repository tracks them separately.

| Host | Skill structure | Packaging/install | Activation adapter | Behavior adapter | Published real-model claims |
| --- | --- | --- | --- | --- | --- |
| OpenAI Codex | Verified | Verified | Yes | Yes | No |
| Claude Code | Verified | Verified | Yes | Yes | No |
| Google Antigravity | Verified | Verified | Yes | Yes | No |
| GitHub Copilot | Documented compatible | Direct skill install | Not yet | Not yet | No |

The machine-readable source is [`compatibility/hosts.json`](../compatibility/hosts.json).

## Meaning of the columns

- **Skill structure**: the canonical `SKILL.md` directory shape is accepted/documented by the host.
- **Packaging/install**: this repository has a host-specific package or a documented direct-install path.
- **Activation adapter**: `scripts/activation_eval.py` can prepare the host for repeated automatic-selection experiments.
- **Behavior adapter**: `scripts/live_eval.py` can run real RED/GREEN behavior experiments for the host.
- **Published real-model claims**: version-bound, sanitized empirical claims exist in `evidence/registry.json`.

A host is not called empirically verified merely because its files package correctly.

## Product caveats

Host discovery behavior can vary by product surface and version. For example, local and managed/cloud products may not expose the same project-skill discovery paths at the same time. Keep product-specific caveats in installation docs and re-test after major host/model changes.
