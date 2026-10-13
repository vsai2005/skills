# Verification Evidence Ledger

Use the ledger for non-trivial changes when `scripts/evidence_ledger.py` is available. Evidence IDs bind verification results to commands and candidate state so later work can refer to retained evidence without reconstructing it from conversation history.

## Plan expected evidence

Register checks that should be completed so anything left unrun appears under `Not verified`:

```bash
python3 scripts/evidence_ledger.py plan \
  --label "Unit tests" \
  --command "python3 -m unittest discover -s tests"
```

The command prints an evidence ID. Reuse that ID when the check runs.

## Prefer ledger-executed evidence

Run verification through the ledger when possible:

```bash
python3 scripts/evidence_ledger.py run \
  --id EV-xxxxxxxx \
  --label "Unit tests" \
  -- python3 -m unittest discover -s tests
```

A successful `run` records timestamp, exit code, cwd, Git HEAD, and a content-sensitive working-tree fingerprint. If code changes afterward, that evidence becomes **stale** and moves to `Not verified` until rerun.

An evidence ID is permanently bound to its first command. Reusing a planned ID with a different command is rejected instead of silently replacing the promised check. A locally executed command that returns zero but changes repository state is also **not verified** by default; rerun verification on the resulting candidate. Use `--allow-state-change` only for a deliberate generator/formatter where mutation is part of the intended check.

A successful command outside a Git worktree is **unbound evidence**, not normal `Verified` evidence, because later staleness cannot be proved. Verification bookkeeping under `.verification/` and `PENDING_TESTS.md` is excluded from the code-state fingerprint so updating the ledger itself does not invalidate evidence.

## Use summary-first capture for noisy checks

When a verification command can emit large logs, add `--capture-output`:

```bash
python3 scripts/evidence_ledger.py run \
  --id EV-xxxxxxxx \
  --label "Unit tests" \
  --capture-output \
  -- python3 -m unittest discover -s tests
```

The ledger writes complete stdout/stderr under:

```text
.verification/evidence-artifacts/<evidence-id>/<run>/
```

and prints only a compact summary containing the evidence ID, exit status, duration, retained output sizes, and artifact directory.

The full artifacts remain local and are ignored by this repository's Git configuration. Do not capture secrets or private data merely because the artifact is local; follow the same diagnostic redaction rules as ordinary logs.

### Drill down without rerunning

If the compact result leaves a specific question unanswered, retrieve only the relevant retained range:

```bash
python3 scripts/evidence_ledger.py view \
  --id EV-xxxxxxxx \
  --stream stdout \
  --start-line 120 \
  --line-count 40
```

For the end of a failure trace:

```bash
python3 scripts/evidence_ledger.py view \
  --id EV-xxxxxxxx \
  --stream stderr \
  --tail 60
```

A view is bounded to at most 200 lines. It prints the retained SHA-256 identity and line range with the selected output.

Do **not** rerun an otherwise-current verification command merely because its original output was too large for context. Reuse the Evidence ID and inspect the retained artifact. Rerun only when the candidate changed, the evidence is stale, the command itself must change, or the original execution was invalid.

If `--artifact-dir` is overridden to a path inside the repository outside excluded verification bookkeeping, the resulting artifact files count as repository mutation. This prevents captured output from silently changing the candidate while remaining marked verified.

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

Reports include the Evidence ID beside each state so later investigation can address the exact retained result.

An outstanding pending test must appear under `Not verified`. Do not claim `Not verified: None` while required pending checks remain.

## Completion rule

Use the generated `Verified` / `Not verified` sections in the completion report. Planned, failed, stale, externally recorded, unbound, repository-mutating, and pending checks are all non-verified states.

Keep these distinctions explicit:

- **observation**: what the retained command output or candidate state directly shows;
- **inference**: what you conclude from that evidence;
- **unknown**: what the current evidence does not establish.

Do not edit ledger history to make a result look green. Rerun and append current evidence only when new execution is actually required.
