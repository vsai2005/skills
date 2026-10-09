import json, tempfile, unittest
from pathlib import Path
from scripts.skill_effectiveness import build_registry, classify, load_records

class SkillEffectivenessTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual('BENEFICIAL', classify(0.2,1.1,1.1))
        self.assertEqual('HARMFUL', classify(-0.1,0.9,1.0))
        self.assertEqual('COSTLY', classify(0.01,1.6,1.0))
    def test_registry_is_model_specific(self):
        rows=[]
        for model in ('m1','m2'):
            for run in (1,2):
                rows.append({'provider':'codex','model':model,'skill':'debug-root-cause','mode':'control','status':'completed','score_fraction':0.5,'duration_seconds':10,'run':run})
                rows.append({'provider':'codex','model':model,'skill':'debug-root-cause','mode':'treatment','status':'completed','score_fraction':0.8 if model=='m1' else 0.4,'duration_seconds':11,'run':run})
        reg=build_registry(rows,2)
        by={e['model']:e for e in reg['entries']}
        self.assertEqual('BENEFICIAL',by['m1']['classification'])
        self.assertEqual('HARMFUL',by['m2']['classification'])

    def test_strong_claim_requires_repeated_paired_evidence(self):
        rows=[]
        for run in range(1,6):
            base={'provider':'codex','model':'m','skill':'debug-root-cause','status':'completed','run':run,'campaign_id':'c','scenario_id':'s','case_sha256':'case','skill_sha256':'skill','skill_hashes':{'debug-root-cause':'skill'}}
            rows.append({**base,'mode':'control','score_fraction':0.4,'passed':False})
            rows.append({**base,'mode':'treatment','score_fraction':0.8,'passed':True})
        entry=build_registry(rows,5)['entries'][0]
        self.assertEqual('BENEFICIAL',entry['classification'])
        self.assertTrue(entry['strong_evidence'])
        self.assertGreater(entry['bootstrap_ci'][0],0)
