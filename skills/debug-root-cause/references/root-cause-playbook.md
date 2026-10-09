# Root-Cause Playbook

## Evidence ladder

Move from observation to explanation:

1. Reproduce the symptom.
2. Minimize the reproduction while preserving failure.
3. Find the earliest point where actual state diverges from expected state.
4. Identify the assumption/invariant that should have prevented divergence.
5. Locate the owner of that assumption.
6. Form a falsifiable hypothesis.
7. Write the expected observation if the hypothesis is true and, when practical, a known-good control.
8. Test one causal factor with safe instrumentation, focused tests, or controlled input.
9. Reject the hypothesis when the decision signal does not match; do not patch anyway.
10. Fix the owner, then re-run both the reproduction and nearby cases.

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

## Do not stop at the proximate failure

The first thrown exception, missing mock method, or failed assertion may only be the place where an earlier invalid decision becomes visible. Before fixing that immediate failure, prove that the path should have been reached. See `hypothesis-and-controls.md`.
