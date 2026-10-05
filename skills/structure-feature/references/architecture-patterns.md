# Architecture Patterns

These are adaptable patterns, not mandatory folder structures.

## UI application

Keep rendering/components focused on presentation and interaction. Move reusable business rules, validation schemas, provider calls, and persistence coordination into owners that can be tested without rendering the whole UI.

For React/Next.js, common boundaries include:

```text
feature/
├── components/      presentation
├── actions|api/     request/application boundary
├── domain/          rules/types when the feature owns them
├── data/            persistence/provider access
└── tests/
```

Use only directories the feature actually needs.

## HTTP/backend service

A useful flow is:

```text
transport -> validation -> application/domain -> repository/provider -> response mapping
```

Do not require a class/service layer for a trivial endpoint when the repository does not use one. The value is separation of responsibility, not the number of layers.

## Shared libraries

Shared code should represent a stable shared concept, not simply code used twice. Verify that consumers agree on semantics before centralizing.

## Integrations

Keep provider-specific request/response quirks near the adapter boundary. Convert them into internal domain/application types before they spread across the codebase.
