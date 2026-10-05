# Complexity Budgets

Use budgets as prompts for review rather than hard universal limits.

## Review signals

A unit deserves another look when several are true:

- it has multiple unrelated reasons to change;
- tests require extensive unrelated setup;
- important logic is deeply nested;
- the file mixes UI, networking, validation, storage, and business policy;
- edits repeatedly occur in distant parts of the same file;
- a "misc", "utils", or "manager" module keeps absorbing behavior;
- new feature work routinely adds another boolean flag or branch;
- the unit cannot be named precisely without using "and" several times.

## Line-count heuristics

Line count alone is weak evidence, but useful as a review trigger. For handwritten application source, files above roughly 500 lines deserve inspection; above roughly 800 lines deserve strong justification. Tests, generated code, parser tables, migrations, and schema snapshots often need different thresholds.

A 150-line function with five responsibilities can be worse than a 700-line declarative schema.

## Extraction rule

Extract when the new unit has a clear name/responsibility and independently meaningful behavior. Do not extract merely to satisfy a number.
