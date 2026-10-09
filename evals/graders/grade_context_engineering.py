from pathlib import Path
import sys, unittest
workspace=Path(sys.argv[1])
sys.path.insert(0,str(workspace))
text=(workspace/'profile.py').read_text(encoding='utf-8')
if 'normalize_name' not in text:
    raise SystemExit('profile.py did not reuse naming.normalize_name')
suite=unittest.defaultTestLoader.discover(str(workspace/'tests'))
result=unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
