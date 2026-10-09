#!/usr/bin/env python3
"""Hidden reproducer for SWE-bench Lite pytest-dev__pytest-11143."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

workspace = Path(sys.argv[1]).resolve()
probe = workspace / ".eval-hidden-numeric-docstring.py"
probe.write_text("123\n\ndef test_numeric_prefix_is_not_docstring():\n    assert True\n", encoding="utf-8")
env = os.environ.copy()
env["PYTHONPATH"] = str(workspace / "src") + os.pathsep + env.get("PYTHONPATH", "")
result = subprocess.run(
    [sys.executable, "-m", "pytest", str(probe), "-q"],
    cwd=workspace,
    env=env,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=120,
)
print(result.stdout[-4000:])
probe.unlink(missing_ok=True)
if result.returncode != 0 or "INTERNALERROR" in result.stdout:
    raise SystemExit(1)
print("historical-reproducer=pass")
