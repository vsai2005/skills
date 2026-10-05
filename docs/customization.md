# Customization

The defaults are deliberately conservative. Adapt them to the repository rather than forcing every repository to look alike.

## Good project-specific additions

Put stable local facts in project guidance or a project-specific companion skill:

- canonical test/lint/typecheck commands;
- source/generated/vendor directories;
- package boundaries and allowed dependency directions;
- public API compatibility requirements;
- database migration policy;
- telemetry/logging conventions;
- framework-specific routing/data-access conventions;
- required security review paths.

## Avoid globalizing one incident

If one bug involved the token `Go`, do not add "always special-case Go" to a global debugging skill. Encode the general lesson: classify technology names using a real taxonomy/boundary instead of confusing them with ordinary short tokens.

## Adjusting complexity budgets

The included budgets are review triggers. Change them when the project has strong reasons, for example generated clients, parser tables, schema snapshots, or intentionally monolithic migration files.

Prefer exemptions that are narrow and documented:

```text
Generated API clients under src/generated are excluded from large-file review.
```

rather than weakening the threshold for all source files.

## Adding a new skill

Create a new skill only when there is a recognizable goal with a distinct workflow and trigger boundary. If the behavior is merely one optional branch of an existing workflow, add a reference instead.

Before adding a skill, define:

1. Requests that should activate it.
2. Requests that should not activate it.
3. Decisions it changes compared with normal agent behavior.
4. Evidence that a separate skill is worth its context/maintenance cost.
