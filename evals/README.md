# Evaluations

The repository keeps two complementary eval sets:

- `activation-cases.json`: machine-readable routing fixtures for whether a primary skill should be selected.
- `behavior-cases.json`: machine-readable behavior scenarios and expected outcomes.
- `behavior-cases.md`: the same behavior scenarios in a human-friendly form with scoring guidance.

`python scripts/validate_repo.py .` validates JSON syntax, IDs, referenced skill names, negative activation coverage, and that every bundled skill appears in both activation and behavior coverage.

The repository **does not claim that CI executes live model evaluations**. Run activation/behavior cases through the actual Codex, Claude Code, or other Agent Skills-compatible harness you intend to use, and repeat important cases to measure variance. See [Evaluation Guide](../docs/evaluation.md).
