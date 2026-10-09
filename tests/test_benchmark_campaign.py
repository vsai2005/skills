import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_campaign import analyze_campaign, load_policy, plan_campaign
from scripts.eval_provenance import sha256_json, sha256_tree

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkCampaignTests(unittest.TestCase):
    def test_full_plan_counts_all_empirical_arms(self):
        policy = load_policy(ROOT / "evals" / "benchmark-policy.json")
        plan = plan_campaign(ROOT, policy, provider="codex", models=["m"], runs=5, profile_name="full", cid="c1")
        self.assertEqual(170, plan["counts"]["local_arms"])
        self.assertEqual(20, plan["counts"]["historical_arms"])
        self.assertEqual(160, plan["counts"]["composition_arms"])
        self.assertEqual(350, plan["counts"]["total_arms"])

    def test_analysis_publishes_only_strong_version_current_evidence(self):
        policy = load_policy(ROOT / "evals" / "benchmark-policy.json")
        skill = "debug-root-cause"
        skill_hash = sha256_tree(ROOT / "skills" / skill)
        case_hash = sha256_json({"id": "case"})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "local").mkdir()
            path = out / "local" / "codex-runs.jsonl"
            rows = []
            for run in range(1, 6):
                common = {
                    "schema_version": 2, "campaign_id": "c1", "provider": "codex", "model": "m",
                    "skill": skill, "scenario_id": "case", "case_sha256": case_hash,
                    "skill_sha256": skill_hash, "skill_hashes": {skill: skill_hash}, "run": run,
                    "status": "completed", "duration_seconds": 10, "usage": {"total_tokens": 100},
                    "workflow_metrics": {"diff_churn": 10, "unrelated_file_count": 0},
                }
                rows.append({**common, "mode": "control", "score_fraction": 0.5, "passed": False})
                rows.append({**common, "mode": "treatment", "score_fraction": 0.8, "passed": True})
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            summary = analyze_campaign(ROOT, out, policy)
            self.assertEqual(1, summary["strong_current_entries"])
            registry = json.loads((out / "effectiveness-registry-strong.json").read_text(encoding="utf-8"))
            self.assertEqual("BENEFICIAL", registry["entries"][0]["classification"])
            self.assertEqual("current", registry["entries"][0]["freshness"])


if __name__ == "__main__":
    unittest.main()
