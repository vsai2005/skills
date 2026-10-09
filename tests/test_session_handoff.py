from pathlib import Path
import subprocess, tempfile, unittest
from scripts.session_handoff import make_handoff, render_markdown

class SessionHandoffTests(unittest.TestCase):
    def test_records_git_state_and_pending_without_source_dump(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'config','user.email','t@example.com'],check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','T'],check=True)
            (root/'a.py').write_text('x=1\n',encoding='utf-8')
            subprocess.run(['git','-C',str(root),'add','a.py'],check=True); subprocess.run(['git','-C',str(root),'commit','-qm','base'],check=True)
            (root/'a.py').write_text('x=2\n',encoding='utf-8')
            (root/'PENDING_TESTS.md').write_text('- [ ] `npm run e2e` — before merge\n',encoding='utf-8')
            data=make_handoff(root,goal='finish',scope=['a.py'],decisions=['keep API'],remaining=['e2e'],failures=[],evidence=['EV-1'],docs=['AGENTS.md'],notes=[])
            self.assertTrue(data['git_head'])
            self.assertIn('a.py',data['changed_files'])
            self.assertTrue(data['pending_tests'])
            text=render_markdown(data)
            self.assertIn('keep API',text); self.assertNotIn('x=2',text)

if __name__=='__main__': unittest.main()
