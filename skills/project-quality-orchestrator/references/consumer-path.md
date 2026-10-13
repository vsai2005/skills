# Consumer-Path Audit

Use this reference when correctness must be traced from a canonical source to what a user or downstream system actually consumes.

## Build the path

Map only layers that exist:

```text
canonical source -> transformation/projection -> delivery boundary -> consumed output
```

Examples:

- source -> generated JSON -> API -> browser;
- schema -> migration -> database;
- Markdown -> build -> published docs;
- configuration -> generated manifest -> runtime;
- model input -> transformation -> exported artifact.

Do not invent browser/server/database/build layers that are not part of the product.

## Inspect meaning-changing boundaries

Check layers that can alter meaning, such as:

- generation/projection;
- cache/serialization;
- API payloads;
- build/export output;
- rendered UI;
- persisted state;
- runtime behavior.

A source-level check does not prove the consumed artifact. Likewise, do not demand browser evidence for a library/CLI/backend-only requirement.

## User-facing truth

When the requirement concerns layout, wording, interaction, accessibility, visual hierarchy, generated content, or another user-visible property, inspect rendered/runtime evidence when feasible.

Delegate detailed UI judgment to `ui-ux-quality`.

If runtime evidence cannot be obtained, state that limitation rather than presenting source inspection as proof.

## Repeated defects

When the same defect appears in several places, test whether a shared template, component, generator, projection, policy, schema, or transformation owns it:

```text
repeated symptom -> shared owner -> general repair -> representative regression checks
```

Do not force a global abstraction when the cases are genuinely independent.

## Semantic artifacts

For diagrams, labels, instructions, generated summaries, workflows, and similar artifacts, verify whether the consumer is likely to infer the intended relationship or action. Syntax-valid output can still be semantically wrong.

## Domain boundaries

Keep project-specific rules in project guidance, fixtures, adapters, or task context. This generic skill coordinates evidence; it must not encode one project's domain vocabulary as universal policy.
