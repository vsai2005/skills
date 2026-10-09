# Context Hygiene

Long sessions accumulate stale plans, duplicate explanations, and abandoned hypotheses.

## Prefer current state

When conversation history and repository state disagree, inspect the repository and use the current state unless the user explicitly asks to restore an earlier decision.

## Compact at boundaries

Before a long pause, model switch, or new session, preserve only:

- goal and accepted scope;
- current Git state;
- important decisions and their reasons;
- changed files;
- remaining work;
- known failures;
- verification evidence and pending checks.

Do not preserve raw exploration when a concise decision record is enough.

## Re-open only when needed

A handoff should point to relevant source/docs rather than embedding large copies of them.
