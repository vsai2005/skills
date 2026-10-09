# Using the Skills Effectively

## Prefer explicit invocation for important work

Automatic activation depends on the host and model. For a critical change, name the skill:

```text
Use debug-root-cause for this regression. Preserve the failing test, find the owning rule, and do not hardcode the provided examples.
```

## Give project facts separately

A reusable skill cannot know your exact build commands or architecture. Combine it with project guidance:

```text
Use structure-feature.
Project constraints:
- run pnpm test:unit and pnpm typecheck;
- src/generated is generated and must not be edited;
- domain may not import web;
- API compatibility is required for v1 clients.
```

## Do not invoke every skill at once

More instructions are not automatically better. Use one specialized skill for a focused task. Use `engineering-quality` when the task truly spans several modes.

## Treat scanners as prompts

If `audit_structure.py` reports a 900-line file, inspect whether it is actually problematic. Generated code, migrations, declarative schemas, and tests can be legitimately large. The skill's qualitative ownership rules matter more than any numeric threshold.

## Use adaptive rigor and pace

Do not force the same ceremony onto every task. `engineering-quality` classifies work from L0 (trivial) through L4 (long-horizon), then chooses FAST/BALANCED/THOROUGH as a separate pace axis. Risk sets the minimum safety floor; pace only changes optional depth. Escalate for shared/high-risk contracts; de-escalate when a task is obviously local.

## Build context selectively

Use `context-engineering` when repository-specific facts are likely to change the implementation. `scripts/repo_context.py` is a deterministic starting map; it intentionally does not dump file contents.

## Ground changing external behavior

Use `source-grounded-development` only when correctness depends on a changing external API/framework/service. Detect the local version first, prefer authoritative versioned sources, then still verify the integration locally.

## Use security hardening at trust boundaries

Use `security-hardening` when attacker-controlled input/state crosses authentication, authorization, secret, file, command, network, deserialization, value-transfer, or similar trust boundaries. Test realistic abuse cases and repair the owning control rather than adding caller-specific deny lists.

## Use a fresh review for high-risk work

For auth/security, migrations, public contracts, architecture changes, or similar high-blast-radius work, use `independent-review` with the original request, final diff, contracts and verification evidence—not the implementer's reasoning narrative. Bind important review results to the exact diff with `scripts/review_state.py`; substantive changes make old review evidence stale.

## Hand off long tasks compactly

Use `scripts/session_handoff.py` at session/model boundaries instead of carrying raw conversation history forward.
## Write technical prose with controlled English

Use `asd-ste100-writing` for procedures, explanations, release notes, review comments, prompts, or user-facing engineering text that must be clear and consistent. The default is about 80% strictness: short direct sentences, stable terminology, and clear conditions without making the prose unnecessarily mechanical. Preserve exact code/API identifiers, UI labels, commands, numbers, warnings, and quoted contract text. The skill is ASD-STE100-inspired and does not claim certified compliance.
## Humanize prose without inventing a person

Use `humanizer-writing` when accurate prose feels stiff, repetitive, overly templated, generically polished, or needs to match an authentic writing sample. Audit before rewriting, use the smallest useful Light/Standard/Deep intensity, and stop when the source is already natural. Preserve facts, uncertainty, identifiers, citations, negation, and the author's actual point of view. For long documents, keep a compact continuity ledger. Do not add fake anecdotes, first-person experience, typos, or AI-detector-evasion language. For technical procedures, use `asd-ste100-writing` first when controlled clarity is required, then humanize lightly without undoing terminology or safety instructions.


## Measure and prune workflow

Use `benchmark_campaign.py` for repeated real-model campaigns, then `skill_effectiveness.py` to see whether a version-matched skill helps a specific model enough to justify its cost. Use executable composition cases to catch skill interference and instruction ablation to remove sections that do not measurably help. Never use benchmark results to bypass a mandatory security or contract check for the task at hand.
