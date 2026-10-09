---
name: context-engineering
description: Prepare the smallest high-value repository context for a coding task when the codebase is unfamiliar, large, convention-heavy, or the current context is stale/noisy. Use before implementation when project-specific rules, nearby precedents, tests, contracts, or version facts are needed to avoid generic or wrong-repository changes. Do not use for trivial local edits with obvious ownership.
---

# Context Engineering

Build the **minimum sufficient context** for the task. More context is not automatically better.

## 1. Decide whether context work is needed

Use this workflow when one or more are true:

- the repository is unfamiliar or large;
- local conventions materially affect the change;
- several possible owners/implementations exist;
- the current session contains stale or contradictory assumptions;
- the task crosses a shared contract or integration boundary.

Skip it for obvious L0 edits such as a typo, local rename, or one-line mechanical change.

## 2. Build a compact context map

Prefer, in order:

1. applicable repository instructions;
2. exact dependency/runtime versions relevant to the task;
3. the likely owning module/files;
4. one strong nearby precedent;
5. tests that protect the same behavior;
6. relevant public types/contracts;
7. only the documentation needed for the change.

Use [references/context-selection.md](references/context-selection.md). `scripts/repo_context.py` can produce a deterministic starting map.

## 3. Read for ownership, not volume

Answer these questions before editing:

- Where does this responsibility live today?
- Which local pattern is considered good practice?
- Which tests would fail for the wrong implementation?
- Which contracts must remain stable?
- Which files are generated/vendor and should not be edited?

Do not recursively load unrelated directories just because they exist.

## 4. Remove stale and irrelevant context

When context becomes noisy:

- discard obsolete plans and superseded assumptions;
- prefer current repository state over old conversation claims;
- keep decisions that still constrain the task;
- summarize long exploration into a compact handoff/state note.

See [references/context-hygiene.md](references/context-hygiene.md).

## 5. Stop when the map is sufficient

Do not keep browsing after ownership, constraints, precedent, tests, and contracts are clear. Continue with the task using the appropriate specialist skill.

For long work or session boundaries, use `scripts/session_handoff.py` and [assets/context-map.md](assets/context-map.md).
