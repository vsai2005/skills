# Cross-host Portability

Core `SKILL.md` instructions stay provider-neutral. Host-specific UI/installation metadata lives in plugin manifests or `agents/` metadata.

Run:

```bash
python3 scripts/portability_check.py . --warnings-as-errors
```

The smoke check validates portable manifests, minimal frontmatter, per-skill OpenAI metadata, provider-neutral core instructions, and obviously non-portable Markdown paths. It does not claim behavioral equivalence across hosts; use the live evaluators for that.

## Self-contained selective installs

A portable skill must carry every file it names. The validator resolves explicit `scripts/`, `references/`, and `assets/` paths from the skill root and fails on missing resources.

Executable helpers that belong to one skill live under that skill's `scripts/` directory. Root-level scripts with the same purpose are compatibility entry points for repository users and delegate to the skill-local canonical implementation.

## Spec vs repository policy

The public Agent Skills specification accepts optional frontmatter fields such as `license`, `compatibility`, `metadata`, and experimental `allowed-tools`. This repository recognizes the public field set, then applies its own stricter portability policy: shipped core skills keep only `name` and `description` in frontmatter.

A repository-policy warning is not presented as a standards violation.

See [Host support matrix](host-support.md) for structural versus empirical support by host.
