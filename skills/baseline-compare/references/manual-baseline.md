# Manual Baseline Reconstruction

A manually repaired historical checkout is weaker evidence because the repair can change behavior.

## Required change log

List every modification, including:

- dependency/version edits;
- lockfile changes;
- config/environment changes;
- fixture/data edits;
- source compatibility patches;
- test-runner configuration changes;
- service/container substitutions.

For each change, record:

```text
Change:
Why required:
Why it should not alter the failure classification:
```

Do not summarize several baseline edits as "made it run." The reviewer needs the full delta to judge equivalence.

If equivalence cannot be defended, classify the comparison as inconclusive rather than calling failures pre-existing.
