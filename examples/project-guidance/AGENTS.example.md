# Example Project Guidance

Use the installed engineering-quality skills for software changes. This file contains only facts specific to this repository.

## Architecture

- `src/domain` owns business rules and must not import `src/web` or provider SDKs.
- `src/providers` translates external provider requests/responses into internal types.
- `src/generated` is generated; do not edit it manually.
- Shared utilities must not contain feature-specific branching.

## Required checks

For TypeScript changes:

```bash
pnpm typecheck
pnpm lint
pnpm test
```

For API-contract changes, also run:

```bash
pnpm test:integration
```

## Compatibility

- `/api/v1` response shapes are backward compatible unless the task explicitly approves a breaking change.
- Database migrations must support rolling deployment between the previous and current app versions.

## Security

- Authorization belongs on the server boundary; UI visibility is not authorization.
- Never log access tokens, refresh tokens, session cookies, or raw secrets.

## Local exceptions

- Large generated OpenAPI clients under `src/generated` are exempt from handwritten-source line-count review.
