---
name: project-quality-orchestrator
description: Coordinate broad cross-layer audits, release/freeze readiness, or repeated systemic defects where correctness must be traced to the final consumed output. Not for ordinary final-diff readiness.
---

# Project Quality Orchestrator

Treat the artifact that users or downstream systems actually consume as the final truth. Source intent is necessary evidence, but it is not sufficient evidence.

## 1. Define the quality contract

Identify:

- the requested outcome and observable acceptance criteria;
- the canonical source of truth;
- every material transformation between source and consumer;
- the final user-visible or machine-consumed artifact;
- explicit non-goals and preserved contracts;
- risk level and required evidence.

Use a compact map:

```text
source -> transformation/projection -> delivery boundary -> consumed output
```

Examples include source -> generated JSON -> API -> browser, schema -> migration -> database, Markdown -> build -> published docs, configuration -> generated manifest -> runtime, or model input -> transformation -> exported artifact.

Do not assume every project has a browser, server, database, or build step.

## 2. Select the smallest useful specialists

Delegate rather than copy their full rules:

- multi-mode implementation -> `engineering-quality`; do not load it merely because this orchestrator is active;
- repository context uncertainty -> `context-engineering`;
- external/version-sensitive facts -> `source-grounded-development`;
- cheap/heavy verification planning -> `tiered-testing`;
- security/trust boundaries -> `security-hardening`;
- user-facing UI/UX quality -> `ui-ux-quality`;
- clear technical prose -> `asd-ste100-writing`;
- natural fact-preserving prose -> `humanizer-writing`;
- high-risk fresh-context review -> `independent-review`;
- final evidence gate -> `verify-change`.

Load only the specialists justified by the current phase. Default to at most 1-2 specialists in a phase. Add another only when a concrete risk, failed check, or required evidence justifies it. Do not preload specialists for possible future work, and do not stack the whole pack by default.

## 3. Verify source to consumed output

For each important requirement, trace the actual path from canonical source to consumed output.

Check intermediate layers only when they exist and can change meaning, for example:

- generated or projected data;
- caches and serialization;
- server/API payloads;
- build outputs;
- rendered UI;
- exported files;
- database state;
- runtime behavior.

A source-level test does not prove a rendered or transformed artifact is correct. Conversely, do not require browser evidence for a CLI, library, or backend-only task unless a browser is genuinely part of the consumer path.

## 4. Prefer rendered or runtime truth for user-facing behavior

When the requirement concerns layout, wording, interaction, accessibility, visual hierarchy, generated content, or another user-visible property, inspect the real rendered/runtime result when feasible.

For a substantial interface-quality review, delegate the UI-specific judgment to `ui-ux-quality` instead of expanding this orchestrator into a design checklist.

Use screenshots, browser/e2e checks, accessibility inspection, exported artifacts, or equivalent evidence appropriate to the product.

If the real environment cannot be exercised, state that limitation. Do not present simulated or source-only inspection as runtime proof.

## 5. Escalate repeated defects to shared causes

When the same defect pattern appears in several places, stop patching instances and test whether a shared template, generator, projection, component, policy, schema, or transformation owns the problem.

Prefer:

```text
repeated symptom -> shared owner -> general repair -> representative regression checks
```

Do not force a global abstraction when the cases are genuinely independent.

## 6. Patch before rewrite

Preserve working architecture and content unless evidence shows the owning model is wrong. Prefer the smallest general repair that fixes the violated invariant.

Rewrite a subsystem only when local patches would preserve the wrong abstraction, create compatibility debt, or make verification harder.

## 7. Match verification to the consumer path

Use the cheapest evidence that can falsify the requirement, then expand with risk.

Examples:

- library/API: focused tests -> integration/contract tests -> consumer checks;
- web UI: component/integration -> build -> browser/e2e -> rendered inspection;
- docs: source checks -> build -> published/rendered inspection;
- data pipeline: unit -> transformation/schema -> persisted/output validation;
- generated artifact: source -> generator -> generated file -> consumer validation.

Use `tiered-testing` only when test-cost/deferment decisions are material. Use `verify-change` only at the final evidence gate; do not keep either loaded through unrelated implementation phases.

## 8. Review semantic correctness, not only syntax

A technically valid artifact can still teach, communicate, visualize, or represent the wrong mental model.

For diagrams, instructions, labels, workflows, generated summaries, and other semantic artifacts, ask whether the consumer is likely to infer the intended relationship or action.

Do not claim deterministic tools can prove semantic correctness when human/model review is required.

## 9. Keep domain rules outside the generic skill

Project-specific rules belong in project guidance, adapters, fixtures, or task context.

Examples of domain-specific extensions include curriculum sequencing, financial reconciliation rules, medical workflow constraints, deployment topology, or a product's design system.

This skill coordinates evidence across layers. It must not encode one project's vocabulary or workflow as a universal rule.

## 10. Apply a release/freeze gate

Before calling a substantial project ready, require evidence appropriate to the actual path:

- canonical source is correct;
- transformations/projections are synchronized;
- relevant static/unit/integration checks pass;
- build/export succeeds when applicable;
- runtime/e2e evidence exists when applicable;
- rendered/consumed output was inspected when the requirement is user-facing;
- important independent-review findings are resolved or dispositioned;
- required deferred tests are cleared or explicitly reported;
- final evidence matches the current candidate state.

Not every item applies to every project. Mark non-applicable gates rather than inventing evidence.

## 11. Report evidence and limits

Finish with:

- what changed or was audited;
- which consumer paths were checked;
- specialists used;
- verification actually completed;
- findings fixed and findings remaining;
- evidence that could not be obtained;
- final readiness decision with explicit conditions.

Never convert confidence, simulation, source inspection, or green unit tests into a stronger claim than the evidence supports.
