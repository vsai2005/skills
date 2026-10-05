# Refactor Plan

## Structural problem

Name the debt precisely.

## Preservation boundary

- Public interfaces:
- User-visible behavior:
- Data/storage:
- Error semantics:

## Behavior lock

Existing or new checks that characterize the current contract.

## Destination ownership

| Responsibility | Current location | Destination | Why |
| --- | --- | --- | --- |
|  |  |  |  |

## Sequence

1. Lock behavior.
2. Create/expose seam.
3. Move one responsibility.
4. Verify.
5. Reroute callers.
6. Remove dead old path.

## Completion evidence

- Preservation checks:
- Structure improvement:
- Dead code removed:
