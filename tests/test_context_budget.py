from pathlib import Path
import unittest

from scripts.context_budget import measure, summarize, violations


ROOT = Path(__file__).resolve().parents[1]


class ContextBudgetTests(unittest.TestCase):
    def test_current_repository_is_within_declared_budget(self):
        budgets = measure(ROOT)
        stats = summarize(budgets)
        self.assertEqual(15, stats["skills"])
        self.assertGreater(stats["total_resource_bytes"], 0)
        self.assertEqual(
            [],
            violations(
                budgets,
                max_total_discovery_chars=7000,
                max_description_chars=600,
                max_skill_lines=500,
                max_resource_bytes=50000,
                max_total_resource_bytes=300000,
            ),
        )

    def test_tight_budget_reports_violation(self):
        budgets = measure(ROOT)
        problems = violations(
            budgets,
            max_total_discovery_chars=1,
            max_description_chars=1,
            max_skill_lines=1,
            max_resource_bytes=1,
            max_total_resource_bytes=1,
        )
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
