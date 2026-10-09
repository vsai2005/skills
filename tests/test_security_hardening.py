import shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class SecurityHardeningTests(unittest.TestCase):
    def test_hidden_security_grader_rejects_bypass_and_accepts_general_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws=Path(tmp)/'ws'; shutil.copytree(ROOT/'evals/live-fixtures/security-hardening',ws)
            grader=ROOT/'evals/graders/grade_security_hardening.py'
            bad=subprocess.run(['python3',str(grader),str(ws)],capture_output=True,text=True)
            self.assertNotEqual(0,bad.returncode)
            (ws/'access.py').write_text('''def can_update_project(actor_id: str, actor_role: str, current_owner_id: str, requested_owner_id: str) -> bool:\n    return actor_role == "admin" or actor_id == current_owner_id\n\ndef update_project_owner(actor_id: str, actor_role: str, current_owner_id: str, requested_owner_id: str) -> str:\n    if not can_update_project(actor_id, actor_role, current_owner_id, requested_owner_id):\n        raise PermissionError("forbidden")\n    return requested_owner_id\n''',encoding='utf-8')
            good=subprocess.run(['python3',str(grader),str(ws)],capture_output=True,text=True)
            self.assertEqual(0,good.returncode,good.stdout+good.stderr)
