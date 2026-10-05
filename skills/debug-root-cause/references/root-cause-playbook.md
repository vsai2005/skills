# Root-Cause Playbook

## Evidence ladder

Move from observation to explanation:

1. Reproduce the symptom.
2. Minimize the reproduction while preserving failure.
3. Find the earliest point where actual state diverges from expected state.
4. Identify the assumption/invariant that should have prevented divergence.
5. Locate the owner of that assumption.
6. Form a falsifiable hypothesis.
7. Test the hypothesis with instrumentation, focused tests, or controlled input.
8. Fix the owner, then re-run both the reproduction and nearby cases.

## Useful narrowing techniques

- compare working and failing inputs;
- inspect recent relevant diffs;
- binary search/bisect when a regression window exists;
- temporarily instrument boundaries, not every line;
- isolate external provider behavior with recorded/reproducible responses;
- reduce concurrency when testing race hypotheses;
- inspect state transitions rather than only final output.

## Five Whys

Five Whys can help but should not become ritual. Stop when the explanation reaches a correctable engineering rule or external constraint with evidence. Do not invent deeper causes merely to reach five levels.
