# Refactoring Strategies

Choose the strategy that directly addresses the named debt.

## Extract coherent responsibility

Use when one unit owns several independently changing concerns. Extract by semantic responsibility, not arbitrary line ranges.

## Introduce adapter boundary

Use when provider/framework-specific details leak across the application. Keep translation and compatibility near the external boundary.

## Consolidate duplicated rule

Use when copies represent the same semantic policy. First verify that differences are accidental, not domain distinctions.

## Split read/write or command/query paths

Use when one abstraction becomes complicated because reads and writes have materially different behavior. Do not apply CQRS ceremony to trivial code.

## Replace flag-driven behavior

A function accumulating boolean flags may represent several concepts. Consider separate named operations or a strategy only when semantics are genuinely distinct.

## Strangler migration

Useful for large legacy replacements: route a bounded slice through the new path, verify it, then expand. Define the removal condition for the old path.

## Mechanical modernization

Dependency/API upgrades are safest when mechanical changes are separated from product behavior changes. Keep compatibility shims at clear boundaries and delete them when the migration completes.
