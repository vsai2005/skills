# Changelog

All notable changes to this project will be documented here.

## 1.0.1 - 2026-10-05

### Fixed

- `audit_structure.py` now fails on missing/non-directory roots instead of reporting a false clean result.
- `diff_guard.py` now includes untracked working-tree files by default and reports their count.
- Repository validation now executes activation/behavior eval validation, checks `VERSION` against every manifest, validates host skill paths, detects orphaned skill resources, and verifies `FILE_MANIFEST.txt` hashes/sizes.
- Codex and portable manifests now explicitly declare `./skills/`.
- `refactor-safely` now links its migration/contract guidance.
- Skill templates and case studies now live inside the owning skill so selective installation keeps them.
- Activation eval routing coverage now includes direct, indirect, incomplete, ambiguous, trivial, and negative cases; the questionable test-only case no longer forces `verify-change`.
- Behavior evals now cover all six bundled skills and have a machine-readable JSON form.
- Self-audit CI no longer excludes the entire test tree.
- The structure scanner now recognizes more common source extensions, focused/skipped tests, `@ts-expect-error`, `console.debug`, and debugger breakpoints.
- Compatibility docs now point to current OpenAI plugin guidance instead of using the deprecated OpenAI skills repository as the primary reference.
- Release manifests no longer claim an impossible self-size/hash, and checksums use portable archive basenames rather than `/mnt/data` paths.

### Added

- Deterministic `generate_manifest.py` and `package_release.py` release tooling.
- Release/package tests and edge-case regression tests for all audit findings.

## 1.0.0 - 2026-10-05

### Added

- Six focused engineering-quality skills with progressive disclosure.
- Portable OpenAI Agent Plugin, Codex compatibility, and Claude Code plugin manifests.
- Repository/skill validator, heuristic structure auditor, and Git diff scope guard.
- Activation/evaluation cases, templates, examples, CI, contribution guidance, and security policy.
