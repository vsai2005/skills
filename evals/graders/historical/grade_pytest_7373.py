#!/usr/bin/env python3
"""Hidden reproducer for SWE-bench Lite pytest-dev__pytest-7373."""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

workspace = Path(sys.argv[1]).resolve()
probe_dir = workspace / ".eval-hidden-skipif"
probe_dir.mkdir(exist_ok=True)
(probe_dir / "test_a.py").write_text(
    "import pytest\nflag = True\n@" + "pytest.mark." + "skipif(\"flag\")\ndef test_a():\n    assert False\n",
    encoding="utf-8",
)
(probe_dir / "test_b.py").write_text(
    "import pytest\nflag = False\n@" + "pytest.mark." + "skipif(\"flag\")\ndef test_b():\n    assert True\n",
    encoding="utf-8",
)
env = os.environ.copy()
env["PYTHONPATH"] = str(workspace / "src") + os.pathsep + env.get("PYTHONPATH", "")
result = subprocess.run(
    [sys.executable, "-m", "pytest", str(probe_dir), "-q"],
    cwd=workspace,
    env=env,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=120,
)
print(result.stdout[-4000:])
for path in sorted(probe_dir.glob("*")):
    path.unlink(missing_ok=True)
probe_dir.rmdir()
summary_ok = re.search(r"1 passed.*1 skipped|1 skipped.*1 passed", result.stdout) is not None
if result.returncode != 0 or not summary_ok:
    raise SystemExit(1)
print("historical-reproducer=pass")
