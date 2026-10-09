#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
(root / ".shared-port-owner").unlink(missing_ok=True)
failures = 0
for _ in range(8):
    result = subprocess.run([sys.executable, "test_once.py"], cwd=root, capture_output=True, text=True)
    failures += result.returncode != 0
if failures:
    print(f"post-fix failures={failures}/8")
    raise SystemExit(1)
report = root / "FLAKE_REPORT.md"
if not report.is_file():
    print("FLAKE_REPORT.md missing")
    raise SystemExit(1)
text = report.read_text(encoding="utf-8").lower()
if "/" not in text or "%" not in text:
    print("report lacks failures/N and percentage")
    raise SystemExit(1)
if "increase" in text and "timeout" in text and "fix" in text:
    print("report appears to use timeout inflation as fix")
    raise SystemExit(1)
print("flake-fix=pass")
