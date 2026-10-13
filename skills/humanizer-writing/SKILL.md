---
name: humanizer-writing
description: Improve accurate prose that is stiff, repetitive, generic, or machine-like while preserving meaning and voice. Do not invent experience, errors, citations, or human authorship, and do not optimize for detector evasion.
---

# Humanizer Writing

Make accurate prose feel natural to a real reader without changing meaning. Humanization is editing, not an authorship claim or detector-bypass task.

## 1. Establish the rewrite contract

Identify audience, purpose, genre, requested intensity, protected facts/identifiers, and the actual writing problems.

If the text is already natural and clear, do not rewrite it merely because this skill was selected.

Use [references/rewrite-workflow.md](references/rewrite-workflow.md) for the full diagnostic and rewrite sequence.

## 2. Use the smallest useful intensity

- **Light** -> remove obvious stiffness, repetition, or filler while preserving nearly all wording.
- **Standard** -> default; restructure sentences/paragraphs when useful while preserving meaning and voice.
- **Deep** -> use for strongly templated drafts or evidence-based voice matching; larger structural changes are allowed, but facts and viewpoint stay fixed.

Do not use Deep mode merely because a stronger rewrite is possible.

## 3. Preserve truth before style

Do not change or invent facts, numbers, dates, limits, warnings, requirements, citations, quoted text, technical identifiers, UI labels, commands, file paths, error codes, the author's experience/viewpoint, or obligation/uncertainty such as `must`, `may`, and `cannot`.

Rewrite from the original source rather than a chain of rewrites.

Use [references/preservation-and-continuity.md](references/preservation-and-continuity.md) for protected-content and long-form rules.

## 4. Match voice only from visible evidence

When the user provides representative writing, match observable tendencies such as sentence rhythm, paragraph density, directness, formality, contractions, punctuation, transitions, and vocabulary complexity.

Do not infer identity, demographics, personality, or hidden traits.

Use [references/voice-and-genre.md](references/voice-and-genre.md) and [assets/voice-profile-template.md](assets/voice-profile-template.md) when voice matching is material.

## 5. Fix patterns, not isolated punctuation

Do not ban words, em dashes, semicolons, fragments, or three-item lists by rule. Change them only when their use is excessive, inappropriate, or part of a repeated template.

Prefer specific nouns/verbs, idea-driven paragraphs, and natural sentence-length variation.

Use [references/naturalness-rules.md](references/naturalness-rules.md) and [references/patterns-and-examples.md](references/patterns-and-examples.md) when the diagnosis needs detail.

## 6. Keep naturalness separate from deception

Never add fake anecdotes, emotions, opinions, quotations, citations, customer feedback, benchmarks, test results, typos, or errors to appear "human."

Do not claim human authorship when unknown and do not optimize for Turnitin, GPTZero, or another detector.

## 7. Verify preservation and naturalness separately

For long work, use the [continuity ledger](assets/continuity-ledger.md) instead of relying on the entire conversation.

When repository helpers are available:

```bash
python3 scripts/humanizer_audit.py audit DRAFT.md
python3 scripts/humanizer_audit.py compare DRAFT.md HUMANIZED.md --fail-on-warning
python3 scripts/voice_profile.py VOICE_SAMPLE.md --candidate HUMANIZED.md
```

Treat helper output as heuristic evidence, not an authorship verdict.

Use [assets/humanization-review-checklist.md](assets/humanization-review-checklist.md) before finalizing.

When `asd-ste100-writing` also applies, controlled clarity, exact terminology, and safety wording take precedence over stylistic variation.
