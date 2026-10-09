# Performance Debugging

Do not optimize from code appearance alone. Establish a comparable baseline and profile the real workload first.

## Loop

```text
Define workload
-> measure baseline
-> profile
-> identify dominant cost
-> form hypothesis
-> change one dominant factor
-> remeasure the same workload
```

## Common evidence sources

- CPU profiles/flame graphs;
- allocation or memory-retention profiles;
- database query counts and execution plans;
- network waterfall and payload sizes;
- render/commit traces;
- event-loop or thread-pool saturation;
- lock/contention metrics;
- cache hit/miss ratios.

## Typical root causes

- N+1 queries or duplicate remote calls;
- unnecessary serialization/copying;
- synchronous I/O on a hot path;
- repeated rendering/recomputation;
- unbounded collection growth;
- lock contention;
- pathological algorithm/input combination;
- cache invalidation or low hit rate;
- excessive retries or polling.

## Required before/after evidence

Use the same representative workload, environment, and measurement method when practical. Report both values and uncertainty/noise.

Do not claim a performance improvement from one faster run without a comparable baseline.

## Anti-patterns

- changing several performance variables at once;
- adding caching before proving repeated expensive work exists;
- increasing worker/thread counts without checking contention or downstream limits;
- removing correctness/safety checks to improve a benchmark;
- using microbenchmarks that do not exercise the production bottleneck.
