import shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ContextHandoffLiveTests(unittest.TestCase):
    def test_handoff_grader_prefers_current_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws=Path(tmp)/'ws'; shutil.copytree(ROOT/'evals/live-fixtures/context-handoff-long',ws)
            grader=ROOT/'evals/graders/grade_context_handoff.py'
            bad=subprocess.run(['python3',str(grader),str(ws)],capture_output=True,text=True)
            self.assertNotEqual(0,bad.returncode)
            (ws/'grading.py').write_text('def passes(score: int) -> bool:\n    return score >= 70\n',encoding='utf-8')
            good=subprocess.run(['python3',str(grader),str(ws)],capture_output=True,text=True)
            self.assertEqual(0,good.returncode,good.stdout+good.stderr)
