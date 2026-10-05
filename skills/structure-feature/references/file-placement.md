# File Placement and Ownership

Place code according to who owns the rule, not according to which file is easiest to edit.

## Ownership questions

For a new piece of logic, ask:

1. Is this presentation behavior, application coordination, domain policy, persistence, integration, or infrastructure?
2. Does an existing module already own that concept?
3. Will another feature likely need exactly the same semantic rule?
4. Does putting it here create a dependency in the wrong direction?

## Common smells

- `utils.ts` / `helpers.py` gaining unrelated business decisions;
- React components performing SQL/API-provider policy directly;
- route handlers containing reusable domain validation;
- database repositories formatting user-facing error messages;
- shared libraries importing feature UI code;
- one `types.ts` containing unrelated domain models from the whole application.

## Feature vs layer organization

Neither is universally correct.

Feature-first organization works well when most code changes together by user/domain capability. Layer-first organization can work when the repository has strong stable layers and shared infrastructure.

Follow the repository's existing successful pattern unless the task explicitly includes restructuring.
