# Scope Control

Scope expansion is a signal to investigate, not automatically a failure.

## Reassessment triggers

Re-check the plan when a narrow task unexpectedly requires:

- many unrelated directories;
- several new abstractions;
- widespread type changes;
- database + API + UI changes not implied by the request;
- editing generated/vendor code;
- test changes much larger than production changes;
- new compatibility branches in multiple locations.

## Questions to ask

1. Did the original owner of the rule get misidentified?
2. Is duplicated logic causing one defect to appear in several places?
3. Is a public/shared contract actually changing?
4. Is the task exposing existing architecture debt that must be addressed now, or can it remain a separate concern?
5. Is the agent editing downstream symptoms instead of the upstream rule?

## Narrow is not always safe

Do not optimize for a tiny diff when the general fix belongs in a shared primitive. "Minimal correct change" means minimum unnecessary scope, not minimum line count.
