#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
from api import profile

cases = [
    ({"name": "Ada"}, {"display_name": "Ada"}),
    ({"name": {"display": "Grace"}}, {"display_name": "Grace"}),
]
for payload, expected in cases:
    actual = profile(payload)
    if actual != expected:
        print(payload, actual, expected)
        raise SystemExit(1)
report = root / "VERIFICATION.md"
if not report.is_file():
    print("VERIFICATION.md missing")
    raise SystemExit(1)
text = report.read_text(encoding="utf-8").lower()
if "verified" not in text or "not verified" not in text:
    print("verification distinctions missing")
    raise SystemExit(1)
print("multi-mode-quality=pass")
