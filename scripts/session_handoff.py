#!/usr/bin/env python3
"""Compatibility wrapper for the canonical skill-local helper.

Canonical implementation: skills/context-engineering/scripts/session_handoff.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / "skills/context-engineering/scripts/session_handoff.py"
_SPEC = importlib.util.spec_from_file_location("_skill_session_handoff", _TARGET)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load skill helper: {_TARGET}")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

for _name in dir(_MODULE):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_MODULE, _name)

if __name__ == "__main__":
    raise SystemExit(_MODULE.main())
