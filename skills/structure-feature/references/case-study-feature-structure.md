# Case Study: Add a Feature Without a God Route

## Situation

An existing backend needs an account settings update endpoint.

## Risky implementation

One route handler parses JSON, validates fields, checks authorization, queries the database, normalizes names, calls an external identity provider, formats errors, and emits analytics.

It works, but every future rule change returns to the route.

## Structured implementation

Follow the repository's existing boundaries. A reasonable shape might be:

```text
HTTP route
  -> request schema/validation
  -> account-settings application operation
      -> shared account naming rule
      -> account repository
      -> identity-provider adapter
  -> transport error/response mapping
```

The exact files depend on local conventions. The important property is ownership: transport logic does not become the permanent home of reusable account policy or provider quirks.

## Tests

- domain/unit coverage for normalization/validation rule;
- API coverage for auth + request/response contract;
- integration coverage for provider/persistence behavior when those boundaries are part of the requirement.
