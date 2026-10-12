from pathlib import Path
import tempfile
import unittest

from scripts.context_budget import _resources, measure, summarize, violations


ROOT = Path(__file__).resolve().parents[1]


class ContextBudgetTests(unittest.TestCase):
    def test_current_repository_is_within_declared_budget(self):
        budgets = measure(ROOT)
        stats = summarize(budgets)
        self.assertEqual(16, stats["skills"])
        self.assertGreater(stats["total_resource_bytes"], 0)
        self.assertEqual(
            [],
            violations(
                budgets,
                max_total_discovery_chars=4500,
                max_description_chars=320,
                max_skill_lines=500,
                max_resource_bytes=50000,
                max_total_resource_bytes=300000,
            ),
        )

    def test_generated_bytecode_is_not_counted_as_progressive_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "scripts" / "__pycache__").mkdir(parents=True)
            (skill / "references").mkdir()
            (skill / "scripts" / "helper.py").write_text("print('ok')\n", encoding="utf-8")
            (skill / "scripts" / "__pycache__" / "helper.cpython-312.pyc").write_bytes(b"x" * 1000)
            (skill / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
            count, total, _tokens = _resources(skill)
            self.assertEqual(2, count)
            self.assertEqual(
                len((skill / "scripts" / "helper.py").read_bytes())
                + len((skill / "references" / "note.md").read_bytes()),
                total,
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
