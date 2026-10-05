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
