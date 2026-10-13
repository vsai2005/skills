# Phase-Boundary Context Decision

At a meaningful phase boundary, choose the smallest context action that preserves required state.

## Continue

Use **Continue** when current raw context remains directly useful and is not materially noisy.

Examples:
- investigation is still active;
- the next edit depends on evidence just gathered;
- clearing would immediately force rereads.

## Clear

Use **Clear** when a phase is complete and its durable decisions/evidence are already captured elsewhere.

Clear obsolete exploration, superseded hypotheses, resolved errors, and redundant tool output. Do not clear constraints that still govern the task.

## Handoff

Use **Handoff** when work moves to another session, harness, directory, branch, person, or substantially different task owner.

Capture only durable state:
- goal/scope;
- key decisions;
- changed files;
- remaining work;
- known failures;
- Evidence IDs/pending tests;
- relevant docs.

Use `scripts/session_handoff.py` when a structured handoff helps.

## Subagent

Use **Subagent** only when the work is genuinely independent enough to benefit from isolated context or parallelism.

Good reasons:
- independent research question;
- fresh review of a high-risk boundary;
- separate component investigation with a clear return contract.

Do not use a subagent merely to move tokens out of the parent context. Aggregate token cost can increase.

Require a bounded return:
- conclusion;
- evidence/references;
- unknowns;
- next action if needed.

## Compact

Use **Compact** when relevant prior state must survive but raw history has become too expensive/noisy to keep.

Preserve:
- current goal and acceptance criteria;
- decisions that still constrain work;
- unresolved failures;
- Evidence IDs and artifact locations;
- current Git/candidate state;
- next actions.

Remove resolved exploration and repeated observations.

## Decision order

```text
Need another owner/session/harness? -> Handoff
Independent question benefits from isolation? -> Subagent
Phase complete and old raw context no longer needed? -> Clear
Relevant state must remain but history is noisy? -> Compact
Otherwise -> Continue
```

These are context-management choices, not mandatory workflow stages.
