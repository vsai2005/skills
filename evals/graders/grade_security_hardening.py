#!/usr/bin/env python3
import importlib.util, re, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('access',root/'access.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
# Existing owner/admin must retain intended capability.
assert mod.update_project_owner('alice','member','alice','bob')=='bob'
assert mod.update_project_owner('root','admin','alice','bob')=='bob'
# Attacker cannot become owner by choosing themselves as future state.
try: mod.update_project_owner('mallory','member','alice','mallory')
except PermissionError: pass
else: raise SystemExit('attacker-controlled requested_owner_id still authorizes update')
text=(root/'access.py').read_text(encoding='utf-8')
if re.search(r"mallory|alice|bob",text): raise SystemExit('solution hardcodes fixture identities')
print('security-boundary=pass')
