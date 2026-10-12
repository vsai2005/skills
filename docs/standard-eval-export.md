# Standard Agent Skills eval export

This repository keeps its richer activation, behavior, live, historical, and composition suites centrally under `evals/`.

The public Agent Skills evaluation guide also documents a simpler per-skill `evals/evals.json` shape. To support third-party tooling without copying grading answers into the runtime skill directories, generate compatible files on demand:

```bash
python3 scripts/export_standard_evals.py . --output-dir dist/standard-evals
```

The exporter creates:

```text
dist/standard-evals/<skill>/evals/evals.json
```

Each exported case includes `prompt`, `expected_output`, `files`, and `assertions`, plus `source_case_id` for traceability back to the canonical central suite.

The generated evals are **development artifacts**, not runtime skill resources. They are deliberately kept outside `skills/` so a normal skill installation does not expose expected answers or spend context on evaluation-only material.
