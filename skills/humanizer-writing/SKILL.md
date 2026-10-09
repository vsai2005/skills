---
name: humanizer-writing
description: Improve prose that is accurate but stiff, repetitive, generic, or machine-like by preserving meaning, matching the author's real voice, and changing only what needs improvement. Use for emails, reports, release notes, posts, explanations, and other prose. Do not fabricate personal experience, fake errors, citations, or claims of human authorship, and do not optimize for AI-detector evasion.
---

# Humanizer Writing

Make prose feel natural to a real reader without changing what it means. Humanization is an editing task, not an authorship claim and not an AI-detector-bypass task.

## 1. Diagnose before rewriting

Identify the audience, purpose, genre, and actual problems first.

Look for:

- generic scene-setting before the point;
- repetitive transitions or sentence openings;
- empty praise and vague benefit language;
- mechanically uniform sentence or paragraph rhythm;
- overlong, overformal, or abstract wording;
- repeated summaries that add no information;
- a mismatch between the text and the author's established voice.

If the text is already natural and clear, **do not rewrite it just because this skill was selected**. Return it unchanged or make only the specific requested edit.

See [references/rewrite-workflow.md](references/rewrite-workflow.md).

## 2. Choose the smallest useful intensity

Use one of these modes:

- **Light** — preserve almost all wording; remove obvious stiffness, repetition, or filler.
- **Standard** — default; restructure sentences and paragraphs when needed while preserving voice and meaning.
- **Deep** — use when the draft is strongly templated or when the user supplies an authentic writing sample and wants closer voice matching. Larger structural changes are allowed, but facts and viewpoint remain fixed.

Do not use Deep mode merely because a stronger rewrite is possible.

## 3. Preserve truth before style

Do not change or invent:

- facts, numbers, dates, limits, warnings, requirements, citations, or quoted text;
- technical identifiers, API names, UI labels, commands, file paths, or error codes;
- the author's actual experience, confidence, role, or point of view;
- uncertainty or obligation such as `may`, `must`, `should`, or `cannot`.

Rewrite from the **original source**, not from a chain of previous rewrites. Repeated rewriting compounds semantic drift.

See [references/preservation-and-continuity.md](references/preservation-and-continuity.md).

## 4. Match real voice when evidence exists

If the user supplies 2-3 representative paragraphs, use them as a voice reference.

Observe only visible writing tendencies such as:

- sentence-length range and rhythm;
- paragraph density;
- directness and formality;
- contractions and first/second-person use;
- punctuation habits;
- explicit versus implicit transitions;
- preferred vocabulary complexity.

Do not infer identity, demographics, personality, or hidden traits from a writing sample.

See [references/voice-and-genre.md](references/voice-and-genre.md) and [assets/voice-profile-template.md](assets/voice-profile-template.md).

## 5. Fix only what fired

Do not replace one artificial pattern with another. Words such as `however`, em dashes, semicolons, or three-item lists are not forbidden. Change them only when their use is excessive, inappropriate, or part of a repeated template.

Prefer specific nouns and verbs, natural sentence-length variation, and paragraph structure driven by the idea itself.

See [references/naturalness-rules.md](references/naturalness-rules.md) and [references/patterns-and-examples.md](references/patterns-and-examples.md).

## 6. Separate naturalness from deception

Never add fake:

- anecdotes or first-hand experience;
- emotions or opinions attributed to the author;
- quotations, citations, customer feedback, benchmarks, or test results;
- typos, grammar mistakes, random fragments, or unusual punctuation intended to fool a detector.

Do not claim or imply that the result was written by a human when that fact is unknown. Do not optimize for Turnitin, GPTZero, or another detector.

## 7. Handle long-form work explicitly

For long documents, keep a small continuity ledger with the audience, voice anchors, terminology, protected facts, current argument, and section purpose. Do not depend on a long conversation transcript as the only memory.

Use [assets/continuity-ledger.md](assets/continuity-ledger.md).

## 8. Verify the rewrite

Review naturalness **and** preservation separately.

If repository helpers are available:

```bash
python3 scripts/humanizer_audit.py audit DRAFT.md
python3 scripts/humanizer_audit.py compare DRAFT.md HUMANIZED.md --fail-on-warning
python3 scripts/voice_profile.py VOICE_SAMPLE.md --candidate HUMANIZED.md
```

Treat helper output as heuristic evidence, not a verdict on authorship.

Use [assets/humanization-review-checklist.md](assets/humanization-review-checklist.md) before finalizing.

When `asd-ste100-writing` also applies, controlled clarity and technical precision win over stylistic variation.
