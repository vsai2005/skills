# Trust Boundaries

Load this reference only when the change crosses a security-sensitive boundary.

## Identity and authorization

- Authentication proves an identity; authorization decides whether that identity may perform this operation on this resource.
- Check object/resource ownership, tenant boundaries, role/scope, impersonation/delegation, session freshness, and privilege changes.
- Do not rely on hidden UI controls or client-supplied roles/owners.

## Input to interpretation

Treat data as dangerous when it becomes code, query syntax, template syntax, a shell command, a file path, a URL/network target, a deserialized object, or a dynamic module/plugin name.

Prefer structured APIs/allowlisted capabilities over escaping strings at many callers.

## Files and uploads

Check canonical path ownership, traversal, symlink behavior, overwrite policy, archive extraction, content/size limits, execution permissions, and where uploaded data is later interpreted.

## Network and redirects

For attacker-influenced URLs/hosts, consider SSRF, redirect chains, DNS/IP changes, internal address ranges, credential forwarding, protocol restrictions, and response-size/time limits.

## Secrets and sensitive data

Minimize secret scope and lifetime. Do not log credentials, cookies, authorization headers, private keys, payment data, or unnecessary PII. Redact at the producer boundary rather than hoping every sink remembers.

## Persistence and value transfer

For balances, permissions, quotas, inventory, or durable workflow state, check atomicity, replay, duplicate delivery, race conditions, idempotency keys, stale reads, and rollback behavior.

## Supply chain and execution

Dependency, build, plugin, workflow, and CI changes can widen execution privilege. Review new download/install scripts, mutable action tags, unverified artifacts, postinstall hooks, and secrets available to automation.
