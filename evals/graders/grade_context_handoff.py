#!/usr/bin/env python3
import importlib.util, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); spec=importlib.util.spec_from_file_location('grading',root/'grading.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
assert mod.passes(70) is True
assert mod.passes(69) is False
# stale historical material is context, not an edit target
if 'Historical note 1' not in (root/'OLD_SESSION.md').read_text(encoding='utf-8'): raise SystemExit('stale transcript was rewritten')
print('handoff-context=pass')
