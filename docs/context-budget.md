# Context Budget

Skill quality can degrade when discovery metadata or always-loaded instructions grow without bound. This repository keeps the skill set focused and uses progressive disclosure so detailed material stays in references/assets until needed.

Check the current budget with:

```bash
python3 scripts/context_budget.py . --fail-on-budget
```

The default guardrails are intentionally simple:

- total bundled discovery metadata: at most 7,000 characters;
- one skill description: at most 600 characters;
- one `SKILL.md`: at most 500 lines;
- one skill's progressive-disclosure resources: at most 50 KB;
- all bundled references/assets together: at most 300 KB.

These are repository guardrails, not universal laws. A future change can revise them deliberately with evidence, but should not silently increase always-visible context.

The script reports separate rough token estimates for always-discoverable/core skill text and conditionally loaded references/assets using four characters per token. That estimate is for trend awareness only; real tokenizer counts vary by model and the skills should normally load selectively rather than all at once.
