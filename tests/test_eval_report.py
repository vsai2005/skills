import unittest

from scripts.eval_report import render_markdown, summarize


class EvalReportTests(unittest.TestCase):
    def test_classifies_improvement_and_pairs_runs(self):
        records = []
        for run, control, treatment in [(1, 0.25, 1.0), (2, 0.5, 0.9)]:
            records.append({
                "provider": "codex", "scenario_id": "x", "run": run, "mode": "control",
                "status": "completed", "score_fraction": control, "passed": False,
                "pass_threshold": 0.8, "duration_seconds": 1.0, "usage": {"input_tokens": 100, "output_tokens": 20, "total_cost_usd": 0.01}, "model": "m1", "workflow_metrics": {"changed_file_count": 2, "diff_churn": 5, "unrelated_file_count": 0, "tool_event_count": 3},
            })
            records.append({
                "provider": "codex", "scenario_id": "x", "run": run, "mode": "treatment",
                "status": "completed", "score_fraction": treatment, "passed": True,
                "pass_threshold": 0.8, "duration_seconds": 2.0, "usage": {"input_tokens": 130, "output_tokens": 25, "total_cost_usd": 0.015}, "model": "m1", "workflow_metrics": {"changed_file_count": 3, "diff_churn": 7, "unrelated_file_count": 1, "tool_event_count": 5},
            })
        rows = summarize(records)
        self.assertEqual(1, len(rows))
        self.assertEqual("improved", rows[0]["classification"])
        self.assertGreater(rows[0]["paired_mean_delta"], 0)
        report = render_markdown(rows)
        self.assertIn("Live Skill Evaluation Report", report)
        self.assertIn("Observed overhead", report)
        self.assertEqual(100.0, rows[0]["control_input_tokens"])
        self.assertEqual(130.0, rows[0]["treatment_input_tokens"])
        self.assertEqual('m1', rows[0]['model'])
        self.assertEqual(1.0, rows[0]['treatment_unrelated_files'])
        self.assertIn('Workflow friction signals', report)

    def test_classifies_regression(self):
        rows = summarize([
            {"provider": "claude", "scenario_id": "x", "run": 1, "mode": "control", "status": "completed", "score_fraction": 1.0, "passed": True, "pass_threshold": 0.8, "duration_seconds": 1},
            {"provider": "claude", "scenario_id": "x", "run": 1, "mode": "treatment", "status": "completed", "score_fraction": 0.5, "passed": False, "pass_threshold": 0.8, "duration_seconds": 1},
        ])
        self.assertEqual("regressed", rows[0]["classification"])

    def test_incomplete_arm_is_inconclusive(self):
        rows = summarize([
            {"provider": "codex", "scenario_id": "x", "run": 1, "mode": "control", "status": "completed", "score_fraction": 0.5, "passed": False, "pass_threshold": 0.8, "duration_seconds": 1},
        ])
        self.assertEqual("inconclusive", rows[0]["classification"])


if __name__ == "__main__":
    unittest.main()
