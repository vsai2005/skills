# Case Study: Refactor a Giant Component Without Creating Folder Theater

## Situation

A React component is 1,200 lines and owns:

- data loading;
- form state;
- validation;
- save/retry behavior;
- formatting;
- modal presentation;
- table rendering.

## Bad extremes

**Do nothing:** keep adding hooks and conditionals to the same component.

**Overengineer:** create 25 files, interfaces, factories, and context providers although most extracted units have no independent responsibility.

## Safer refactor

1. Use existing interaction tests to lock save/cancel/error behavior.
2. Extract domain/form validation into the repository's existing schema/validation pattern.
3. Extract data/update coordination into the local feature hook/service pattern if one exists.
4. Extract modal/table presentation only where each component has a coherent UI responsibility.
5. Keep trivial formatting local unless it is semantically shared.
6. Run focused tests after each move.
7. Remove old state/effects/imports after callers move.

## Success criteria

The root component becomes an orchestrator with understandable state flow; extracted units have names that explain their responsibility; public props and behavior remain stable; the project does not gain a new architecture just for one component.
