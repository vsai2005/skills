# Dependency Boundaries

Healthy boundaries make direction predictable.

## General principle

Higher-level policy should not be forced to depend on lower-level delivery/framework details merely because those details are convenient.

Examples:

- domain rule should not need a React component type;
- core business logic should not parse a provider-specific HTTP payload everywhere;
- infrastructure can implement an application/domain-defined port when that separation already fits the project;
- transport/UI can translate external input into internal types.

## Avoid dogma

A small application may legitimately place route and business logic close together. Add boundaries when they clarify ownership/testing/change frequency, not to maximize layer count.

## Shared modules

A shared module should be stable and semantically cohesive. If it imports from many features or grows feature-specific branches, it may be the wrong owner.
