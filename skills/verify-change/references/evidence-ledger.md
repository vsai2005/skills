# Verification Evidence Ledger

Use the ledger for non-trivial changes when `scripts/evidence_ledger.py` is available.

## Plan expected evidence

Register checks that should be completed so anything left unrun appears under `Not verified`:

```bash
python3 scripts/evidence_ledger.py plan \
  --label "Unit tests" \
  --command "python3 -m unittest discover -s tests -v"
```

The command prints an evidence ID. Reuse that ID when the check runs.

## Prefer ledger-executed evidence

Run verification through the ledger when possible:

```bash
python3 scripts/evidence_ledger.py run \
  --id EV-xxxxxxxx \
  --label "Unit tests" \
  -- python3 -m unittest discover -s tests -v
```

A successful `run` records timestamp, exit code, cwd, Git HEAD, and a content-sensitive working-tree fingerprint. If code changes afterward, that evidence becomes **stale** and moves to `Not verified` until rerun.

An evidence ID is permanently bound to its first command. Reusing a planned ID with a different command is rejected instead of silently replacing the promised check. A locally executed command that returns zero but changes repository state is also **not verified** by default; rerun verification on the resulting candidate. Use `--allow-state-change` only for a deliberate generator/formatter where mutation is part of the intended check.

A successful command outside a Git worktree is **unbound evidence**, not normal `Verified` evidence, because later staleness cannot be proved. Verification bookkeeping under `.verification/` and `PENDING_TESTS.md` is excluded from the code-state fingerprint so updating the ledger itself does not invalidate evidence.

## External evidence is not local verification

When another runner executed the command, it can be recorded for traceability:

```bash
python3 scripts/evidence_ledger.py record \
  --label "Browser e2e" \
  --command "npm run e2e" \
  --exit-code 0
```

`record` is deliberately labeled **externally recorded**, not `Verified`, because the ledger did not execute and observe that command itself. Link to CI/artifact evidence separately when available.

## Include deferred required checks

`report` reads `PENDING_TESTS.md` by default when it exists:

```bash
python3 scripts/evidence_ledger.py report
```

An outstanding pending test must appear under `Not verified`. Do not claim `Not verified: None` while required pending checks remain.

## Completion rule

Use the generated `Verified` / `Not verified` sections in the completion report. Planned, failed, stale, externally recorded, unbound, repository-mutating, and pending checks are all non-verified states.

Do not edit ledger history to make a result look green. Rerun and append current evidence instead.
