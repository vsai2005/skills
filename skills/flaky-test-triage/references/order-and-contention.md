# Order and Shared-Resource Checks

## Order dependence

Look for:

- mutable process/global state not reset;
- environment/config mutated by earlier tests;
- database/file fixtures reused without cleanup;
- randomized test order or data seeds;
- module caches/singletons persisting across tests.

Try the failing test alone, immediately after suspected predecessors, and under the suite's normal/randomized order controls.

## Shared-resource contention

Look for collisions in:

- fixed ports;
- shared temp filenames/directories;
- one database/schema/account reused across workers;
- caches or queues with shared keys;
- CPU/thread/process pools;
- clocks/timers/schedulers;
- external sandbox quotas/rate limits.

Compare serial and parallel execution when the runner supports it. A lower failure rate in serial mode is evidence of contention, not proof of the exact cause.
