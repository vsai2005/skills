# Context Selection

Select information because it can change an engineering decision.

## High-value context

- applicable `AGENTS.md`, `CLAUDE.md`, Cursor/Copilot project instructions;
- package/runtime manifests and lockfile-derived versions;
- the likely owner of the changed behavior;
- one representative local implementation with similar semantics;
- focused tests around the same rule;
- public interfaces, schemas, migrations, provider boundaries, or security rules touched by the change.

## Low-value context

- unrelated modules;
- many examples of the same pattern after one good precedent is understood;
- large generated/vendor trees;
- historical discussion that conflicts with current code;
- broad documentation unrelated to the exact dependency/version in use.

## Stopping rule

Stop gathering context when you can name:

```text
owner
local precedent
contracts
relevant tests
version-sensitive facts
verification command
```
