---
name: source-grounded-development
description: Ground implementation decisions in authoritative current sources when correctness depends on a changing external API, framework, SDK, cloud service, database, authentication library, deployment tool, or package version. Use when training-memory knowledge may be stale or version-sensitive. Skip for purely local business logic, algorithms, renames, or refactors whose behavior is fully defined inside the repository.
---

# Source-Grounded Development

Do not guess changing external behavior when the repository or an authoritative source can answer it.

## 1. Identify the version-sensitive dependency

Determine the exact library/service/tool and the version or deployment target in use. Prefer lockfiles, manifests, generated metadata, or explicit project configuration over memory.

## 2. Decide whether external grounding is necessary

Ground externally when the task depends on:

- framework/SDK APIs or configuration;
- recently changed defaults/deprecations;
- cloud/provider behavior;
- authentication/security library behavior;
- database/migration syntax or version capability;
- deployment/build-tool semantics.

Do not invoke external research for behavior fully owned by this repository.

## 3. Use sources in priority order

Follow [references/source-priority.md](references/source-priority.md):

1. local version/configuration evidence;
2. official documentation for that version;
3. official changelog/release notes/source repository;
4. trusted primary technical references;
5. community reports only as supporting evidence.

## 4. Convert source facts into local decisions

Do not paste documentation into code. Record only the facts that affect the implementation, then fit them to the repository's established architecture.

Use [references/version-grounding.md](references/version-grounding.md) when versions differ across local/runtime environments.

## 5. Verify the resulting behavior locally

Documentation is evidence about the external system, not proof that the integration works here. Run the repository's relevant tests/build/runtime checks after implementation.

For substantial decisions, capture the dependency, version, source and implementation implication using [assets/source-record.md](assets/source-record.md).
