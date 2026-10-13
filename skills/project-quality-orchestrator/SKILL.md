---
name: project-quality-orchestrator
description: Coordinate broad cross-layer audits, release/freeze readiness, or systemic defects where correctness must be traced from canonical source to final consumed output. Not for an ordinary final-diff readiness check.
---

# Project Quality Orchestrator

Treat the artifact users or downstream systems actually consume as final truth. Source intent is evidence, not proof.

## 1. Define the quality contract

Identify:

- requested outcome and observable acceptance criteria;
- canonical source of truth;
- material transformations/projections;
- final consumed artifact;
- explicit non-goals and preserved contracts;
- risk level and required evidence.

Start with:

```text
source -> transformation/projection -> delivery boundary -> consumed output
```

Use [references/consumer-path.md](references/consumer-path.md) when the path or semantic correctness needs detailed review.

## 2. Load only justified specialists

Delegate rather than copying specialist rules:

- multi-mode implementation -> `engineering-quality`;
- context uncertainty -> `context-engineering`;
- version-sensitive external facts -> `source-grounded-development`;
- test-cost/deferment -> `tiered-testing`;
- trust/security boundaries -> `security-hardening`;
- UI/UX judgment -> `ui-ux-quality`;
- controlled prose -> `asd-ste100-writing`;
- natural fact-preserving prose -> `humanizer-writing`;
- high-risk fresh-context review -> `independent-review`;
- final evidence gate -> `verify-change`.

Default to at most one or two specialists in a phase. Add another only for a concrete risk, failed check, or required evidence. Do not preload the pack.

## 3. Trace real source-to-consumer behavior

For each material requirement, verify the actual path through only the layers that exist and can change meaning.

Prefer rendered/runtime truth for user-facing requirements when feasible. A source-level check does not prove a transformed/rendered artifact, and a browser is not required when the browser is not part of the consumer path.

When repeated defects appear, test for a shared owner before patching instances.

Use [references/consumer-path.md](references/consumer-path.md) for detailed path examples, runtime/rendered evidence rules, repeated-defect escalation, and semantic-artifact review.

## 4. Repair the owning cause with proportional scope

Prefer the smallest general repair that restores the violated invariant while preserving working architecture and contracts.

Avoid:

- repeated instance patches around a shared defect;
- broad rewrites without evidence that the abstraction is wrong;
- new global abstractions for genuinely independent cases;
- domain-specific policy inside this generic skill.

Project-specific rules belong in project guidance, fixtures, adapters, or task context.

## 5. Match verification to the consumer path

Use the cheapest evidence that can falsify the requirement, then broaden with risk.

Do not keep `tiered-testing` or `verify-change` loaded through unrelated phases.

For substantial release/freeze work, use [references/release-freeze-gate.md](references/release-freeze-gate.md) for the consumer-path verification ladder and final readiness gate.

## 6. Report evidence and limits

Finish with:

- changed/audited scope;
- consumer paths checked;
- specialists actually used;
- verification completed;
- findings fixed and remaining;
- unavailable evidence;
- readiness decision and explicit conditions.

Never promote confidence, simulation, source inspection, or green unit tests into a stronger claim than the evidence supports.
