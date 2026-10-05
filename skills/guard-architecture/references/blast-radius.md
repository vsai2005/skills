# Blast Radius

Blast radius is the set of behavior that can change because a shared rule, contract, or boundary changes.

## Trace dimensions

### Code consumers

Search imports, references, implementations, registrations, reflection/dynamic lookup, and generated clients.

### Data consumers

Check readers/writers, migrations, analytics, cache keys, serialization, and background jobs.

### Protocol consumers

Check REST/GraphQL/RPC schemas, events, webhooks, CLI, plugins, and public library APIs.

### Operational consumers

Check deployment order, env/config, scheduled jobs, queue workers, retries, and rollback.

## Risk increases when

- consumers deploy independently;
- data persists across versions;
- compatibility cannot be coordinated atomically;
- behavior is security- or money-sensitive;
- callers are numerous or dynamic;
- tests cover only one consumer.
