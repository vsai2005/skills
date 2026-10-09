from pathlib import Path
import sys, unittest
workspace=Path(sys.argv[1])
sys.path.insert(0,str(workspace))
text=(workspace/'app.py').read_text(encoding='utf-8')
if 'responses.create' not in text or 'chat.completions' in text:
    raise SystemExit('implementation did not follow v3 source-grounded API')
suite=unittest.defaultTestLoader.discover(str(workspace/'tests'))
result=unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
