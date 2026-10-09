#!/usr/bin/env python3
import ast
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=root)
if result.returncode:
    raise SystemExit(result.returncode)
from web import quote_response
response = quote_response(1000, 10)
if response.get("discount_label") != "10% off":
    print(f"discount label missing/incorrect: {response}")
    raise SystemExit(1)

tree = ast.parse((root / "domain.py").read_text(encoding="utf-8"))
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        if any(alias.name == "web" or alias.name.startswith("web.") for alias in node.names):
            print("domain imports web")
            raise SystemExit(1)
    if isinstance(node, ast.ImportFrom) and node.module and (node.module == "web" or node.module.startswith("web.")):
        print("domain imports web")
        raise SystemExit(1)
print("dependency-direction=pass")
