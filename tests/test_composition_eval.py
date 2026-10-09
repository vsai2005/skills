from pathlib import Path
import unittest
from scripts.composition_eval import ARMS, compare_records, load_cases, plan, main as composition_main
ROOT=Path(__file__).resolve().parents[1]
class CompositionEvalTests(unittest.TestCase):
    def test_cases_validate_and_plan_four_arms(self):
        cases=load_cases(ROOT/'evals/composition-cases.json',ROOT)
        self.assertEqual(8,len(cases))
        rows=plan(cases[:1],'codex',['m1'],2)
        self.assertEqual(8,len(rows))
        self.assertEqual(set(ARMS),{r['arm'] for r in rows})

    def test_dry_run_executes_four_arm_composition_matrix(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            code=composition_main(['run','--provider','codex','--model','m','--runs','1','--case','debug-plus-grounding','--campaign-id','c','--output-dir',tmp,'--dry-run'])
            self.assertEqual(0,code)
            path=Path(tmp)/'codex-composition-runs.jsonl'
            rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(4,len(rows))
            self.assertEqual(set(ARMS),{row['arm'] for row in rows})
            combined=next(row for row in rows if row['arm']=='combined')
            self.assertEqual(['debug-root-cause','source-grounded-development'],combined['enabled_skills'])

    def test_compare_detects_interference(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'runs.jsonl'
            rows=[]
            for run in (1,2,3):
                for arm,score in [('control',0.4),('a-only',0.8),('b-only',0.75),('combined',0.6)]:
                    rows.append({'provider':'codex','model':'m','case_id':'x','arm':arm,'score_fraction':score,'run':run,'status':'completed'})
            path.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
            result=compare_records(path)
            self.assertEqual('INTERFERENCE',result['entries'][0]['classification'])
