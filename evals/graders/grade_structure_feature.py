#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
import routes

if not hasattr(routes, "update_settings_route"):
    print("routes.update_settings_route missing")
    raise SystemExit(1)
result = routes.update_settings_route("u1", "  Ada   Lovelace ")
if result.get("display_name") != "Ada Lovelace":
    print(f"unexpected result={result}")
    raise SystemExit(1)
route_text = (root / "routes.py").read_text(encoding="utf-8")
if "_STORE" in route_text:
    print("route bypasses repository/service ownership")
    raise SystemExit(1)
print("feature-structure=pass")
