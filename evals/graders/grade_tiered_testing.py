#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
pending = root / "PENDING_TESTS.md"
if not pending.is_file():
    print("PENDING_TESTS.md missing")
    raise SystemExit(1)
text = pending.read_text(encoding="utf-8").lower()
if "e2e_check.py" not in text or "before release" not in text:
    print("pending heavy e2e command/trigger not recorded")
    raise SystemExit(1)
print("tiered-testing-pending=pass")
