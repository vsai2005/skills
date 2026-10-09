# Cross-host Portability

Core `SKILL.md` instructions stay provider-neutral. Host-specific UI/installation metadata lives in plugin manifests or `agents/` metadata.

Run:

```bash
python3 scripts/portability_check.py . --warnings-as-errors
```

The smoke check validates portable manifests, minimal frontmatter, per-skill OpenAI metadata, provider-neutral core instructions, and obviously non-portable Markdown paths. It does not claim behavioral equivalence across hosts; use the live evaluators for that.
