#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=root)
if result.returncode:
    raise SystemExit(result.returncode)
source = (root / "reporting.py").read_text(encoding="utf-8")
if len(source.splitlines()) >= 28 and not any((root / name).is_file() for name in ("validation.py", "formatting.py", "reporting_utils.py")):
    print("named structural debt was not reduced")
    raise SystemExit(1)
print("refactor-preservation=pass")
