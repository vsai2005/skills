Cache invalidation is now event-driven. That cuts the stale window without adding another polling loop. There isn't a migration step, so rollout stays straightforward. If metrics move in the wrong direction, the old worker can be restored in one deploy.

The change is small on purpose. It fixes the delay we measured without widening the service boundary or adding a second queue.
