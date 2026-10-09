# Source Priority

Use the strongest source that can answer the exact version-sensitive question.

## Priority

1. **Local repository evidence** — manifests, lockfiles, generated clients, configuration and source currently deployed.
2. **Official versioned documentation** — exact major/minor when available.
3. **Official changelog/release notes/source** — especially for migrations, deprecations and breaking changes.
4. **Primary technical references** — standards, specifications or provider-maintained examples.
5. **Community material** — useful for edge cases or operational reports, but cross-check before treating it as contract.

## Conflicts

If local code and docs disagree, determine whether the repository is on an older version, uses a compatibility layer, or carries a deliberate workaround. Do not silently overwrite local reality with the newest docs.
