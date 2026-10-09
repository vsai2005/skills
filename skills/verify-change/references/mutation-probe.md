# Optional Test-the-Test Mutation Probe

Use this only when a newly added regression test is important and there is a safe, isolated way to perturb the guarded behavior.

## Purpose

A regression test that stays green after the relevant behavior is deliberately broken may not protect the claimed contract.

## Safe protocol

1. Use an isolated worktree or disposable copy; never mutate the review branch in place.
2. Apply one small reversible mutation that should violate the exact new contract (for example invert the newly fixed condition or return the old wrong value).
3. Run only the targeted regression test/check.
4. Confirm it fails for the expected reason.
5. Destroy the disposable worktree/copy; do not carry mutation code into the real diff.

Do not use mutation probes for destructive migrations, irreversible external effects, production systems, or changes where a safe mutation cannot be stated precisely.
