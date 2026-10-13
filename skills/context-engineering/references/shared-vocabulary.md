# Shared Vocabulary

Use an existing project vocabulary source when recurring domain terms affect search, naming, contracts, or handoff quality.

Examples include:

- `GLOSSARY.md`;
- `VOCABULARY.md`;
- `TERMS.md`;
- domain glossary/terms documents;
- established terminology sections in architecture or domain documentation.

## Load vocabulary JIT

Do not preload the whole glossary merely because it exists.

Load only the terms relevant to the current task when they help:

- distinguish similar domain concepts;
- search for the owning implementation;
- preserve canonical names in code or documentation;
- avoid repeating long domain explanations;
- hand work to another agent/session without terminology drift.

A vocabulary document is context, not authority over working code. Reconcile it with current contracts, schemas, tests, and repository behavior when they disagree.

## Do not invent a glossary for token savings

Do not create new terminology or a new glossary solely to shorten prompts.

Create or update a project glossary only when the repository already needs stable shared language for humans and software work. Prefer existing domain names over agent-specific shorthand.

## Keep retrieval bounded

For a large vocabulary source:

1. identify the term(s) relevant to the task;
2. retrieve those entries or the smallest useful section;
3. preserve exact canonical wording where it affects contracts/names;
4. do not keep unrelated definitions in active context.
