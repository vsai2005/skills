# Context Budget

Skill quality can degrade when discovery metadata or always-loaded instructions grow without bound. This repository keeps the skill set focused and uses progressive disclosure so detailed material stays in references/assets/scripts until needed.

Check the current budget with:

```bash
python3 scripts/context_budget.py . --fail-on-budget
```

The default guardrails are intentionally simple:

- total bundled discovery metadata: at most 4,500 characters;
- one skill description: at most 320 characters;
- one `SKILL.md`: at most 500 lines;
- one skill's progressive-disclosure resources: at most 50 KB;
- all bundled references/assets/scripts together: at most 300 KB.

The tighter discovery limits protect the always-visible context budget: skill descriptions should identify activation boundaries, while workflow detail belongs in the selectively loaded skill body or references.

These are repository guardrails, not universal laws. A future change can revise them deliberately with evidence, but should not silently increase always-visible context.

The script reports separate rough token estimates for always-discoverable/core skill text and conditionally loaded references/assets/scripts using four characters per token. That estimate is for trend awareness only; real tokenizer counts vary by model and the skills should normally load selectively rather than all at once.
