#!/usr/bin/env python3
import sys
from pathlib import Path

report = Path(sys.argv[1]).resolve() / "baseline-report.md"
if not report.is_file():
    print("baseline-report.md missing")
    raise SystemExit(1)
text = report.read_text(encoding="utf-8").lower()
required = ["test.preexisting", "pre-existing", "test.regression", "regression"]
missing = [item for item in required if item not in text]
if missing:
    print(f"missing={missing}")
    raise SystemExit(1)
print("baseline-report=pass")
