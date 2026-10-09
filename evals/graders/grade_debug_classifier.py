#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("candidate_classifier", root / "classifier.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
checks = {
    "Go": True,
    "C pointers": True,
    "R data frames": True,
    "Rust ownership": True,
    "Java streams": True,
    "JavaScript arrays": False,
    "React state": False,
    "please explain arrays": False,
}
failed = []
for text, expected in checks.items():
    actual = bool(module.has_foreign_topic(text))
    if actual != expected:
        failed.append((text, expected, actual))
if failed:
    print(f"failed={failed}")
    raise SystemExit(1)
print("generic-classification-checks=pass")
