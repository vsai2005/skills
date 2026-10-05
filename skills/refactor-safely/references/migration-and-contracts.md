# Migration and Contract Safety

Refactors become migrations when persisted data, public APIs, cross-service events, or external consumers are involved.

## Compatibility questions

- Can old and new application versions overlap during deployment?
- Must old data remain readable?
- Are events consumed asynchronously by older consumers?
- Can a schema change be expanded before it is contracted?
- Is rollback required?

## Expand/contract pattern

For compatible schema/API migrations:

1. add new representation while old remains supported;
2. write/translate safely during overlap;
3. migrate/backfill if necessary;
4. switch consumers;
5. verify no old consumers remain;
6. remove legacy representation.

Do not use this pattern mechanically when an atomic internal change is simpler and safe.
