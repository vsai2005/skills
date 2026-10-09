# PENDING_TESTS.md Policy

`PENDING_TESTS.md` is a queue for **required verification that is intentionally deferred**, not a dumping ground for optional ideas.

Each pending item needs:

- exact runnable command;
- reason it cannot/should not run yet;
- trigger that makes it due.

Good triggers: `before merge`, `after browser environment is available`, `before release candidate tagging`.

Bad trigger: `later`.

## Add and inspect

```bash
python3 scripts/pending_tests.py add \
  --command "npm run e2e" \
  --reason "browser environment unavailable in current runner" \
  --trigger "before merge"

python3 scripts/pending_tests.py list
```

## Completion requires proof

Do not remove an item merely because cheaper tests passed. Complete it with current ledger-executed evidence:

```bash
python3 scripts/pending_tests.py complete PT-xxxxxxxx \
  --evidence-id EV-xxxxxxxx
```

The evidence must still be current for the repository state. Stale, failed, planned, or externally recorded evidence does not satisfy completion.

If the exact check is genuinely replaced by an equivalent requirement, use an explicit explanation instead:

```bash
python3 scripts/pending_tests.py complete PT-xxxxxxxx \
  --superseded-by "Replaced by the new cross-browser matrix covering the same acceptance contract"
```

Use supersession sparingly; it is a requirement change, not an escape hatch. CLI completions are appended to `.verification/pending_tests_history.jsonl` so removed queue items still have a local audit trail.

`verify-change` should include remaining pending items in `Not verified`, and release packaging must stop while any pending item remains.
