---
name: asd-ste100-writing
description: Rewrite or draft technical prose in a clear ASD-STE100-inspired controlled-English style for documentation, procedures, explanations, release notes, review comments, prompts, and user-facing engineering text. Use when clarity, consistency, short sentences, direct instructions, and stable terminology matter. Preserve exact code/API identifiers and do not claim certified ASD-STE100 compliance.
---

# ASD-STE100-Inspired Writing

Write clear technical English without changing technical meaning. Use a balanced **80% strictness** by default: follow controlled-English principles strongly, but keep the text natural and readable.

This skill is **ASD-STE100-inspired**. It is not a certification claim and does not reproduce the official ASD-STE100 controlled vocabulary.

## 1. Protect technical meaning first

Do not simplify away:

- requirements, constraints, warnings, limits, numbers, units, or error codes;
- API names, code identifiers, UI labels, file paths, commands, or quoted contract text;
- distinctions between similar technical concepts.

Keep exact technical names unchanged unless the user asks to rename them.

## 2. Use one term for one concept

Choose one clear term and use it consistently.

Do not alternate between synonyms such as `service`, `process`, and `component` when they refer to the same thing.

Define an uncommon domain term when the reader may not know it. Do not invent simpler names for official API or product terms.

See [references/writing-rules.md](references/writing-rules.md).

## 3. Keep sentences short and direct

As house targets for the default 80% mode:

- aim for **20 words or fewer** in procedural instructions;
- aim for **25 words or fewer** in descriptive text;
- keep one main action or idea in each sentence;
- prefer active voice when the actor matters;
- use a direct verb instead of a noun-heavy phrase.

These are review targets, not reasons to damage meaning.

## 4. Write instructions as actions

Prefer direct imperative forms:

```text
Restart the service.
Check the Status indicator.
```

When a condition controls an action, put the condition first:

```text
If error E104 remains, do not change the database configuration.
Contact the support team.
```

Prefer positive instructions when they are equally safe and precise. Keep necessary prohibitions explicit.

## 5. Remove avoidable complexity

Prefer common, concrete wording:

- `use` instead of `utilize`;
- `to` instead of `in order to`;
- `because` instead of `due to the fact that` when grammar permits;
- `now` instead of `at this point in time`.

Avoid vague pronouns when the referent is not obvious. Break long noun clusters into clearer phrases.

See [references/examples.md](references/examples.md).

## 6. Format for scanning

Use:

- numbered steps for ordered procedures;
- bullets for parallel facts or conditions;
- short headings with a clear topic or action;
- tables only when the reader must compare several attributes.

Do not turn simple prose into excessive structure.

## 7. Use balanced strictness

Default to **80% strictness** unless the user asks for stricter controlled English.

At this level:

- enforce terminology consistency, short sentences, direct instructions, and clear conditions;
- allow standard technical terms and familiar transitions when they improve readability;
- do not make the text sound mechanical solely to satisfy a style rule;
- preserve necessary nuance in architecture, security, legal, or safety text.

## 8. Review before delivery

Use [assets/writing-review-checklist.md](assets/writing-review-checklist.md).

Confirm that the result is easier to understand **and** technically equivalent to the source. If clarity and technical accuracy conflict, preserve accuracy and explain the unavoidable complexity only when needed.
