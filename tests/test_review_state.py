import subprocess, tempfile, unittest
from pathlib import Path
from scripts.review_state import snapshot

class ReviewStateTests(unittest.TestCase):
    def test_diff_fingerprint_changes_after_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp); subprocess.run(['git','init','-q',str(r)],check=True); subprocess.run(['git','-C',str(r),'config','user.email','t@example.com'],check=True); subprocess.run(['git','-C',str(r),'config','user.name','T'],check=True)
            (r/'a.py').write_text('x=1\n'); subprocess.run(['git','-C',str(r),'add','.'],check=True); subprocess.run(['git','-C',str(r),'commit','-qm','base'],check=True)
            (r/'a.py').write_text('x=2\n'); a=snapshot(r,'HEAD')
            (r/'a.py').write_text('x=3\n'); b=snapshot(r,'HEAD')
            self.assertNotEqual(a['diff_sha256'],b['diff_sha256'])
            self.assertEqual(40, len(a['base']))
            self.assertNotIn('HEAD', a['base'])
