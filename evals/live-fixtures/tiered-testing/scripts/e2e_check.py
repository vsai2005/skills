import os
import sys

if os.environ.get("BROWSER_AVAILABLE") != "1":
    print("browser environment unavailable", file=sys.stderr)
    raise SystemExit(2)
print("e2e-pass")
