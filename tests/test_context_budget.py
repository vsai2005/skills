from pathlib import Path
import tempfile
import unittest

from scripts.context_budget import (
    _resources,
    budget_warnings,
    compare_summaries,
    measure,
    summarize,
    violations,
)


ROOT = Path(__file__).resolve().parents[1]


class ContextBudgetTests(unittest.TestCase):
    def test_current_repository_is_within_declared_budget(self):
        budgets = measure(ROOT)
        stats = summarize(budgets)
        self.assertEqual(17, stats["skills"])
        self.assertGreater(stats["total_resource_bytes"], 0)
        self.assertEqual(
            [],
            violations(
                budgets,
                max_total_discovery_chars=4500,
                max_description_chars=320,
                max_skill_lines=500,
                max_skill_tokens=2500,
                max_resource_bytes=50000,
                max_total_resource_bytes=300000,
            ),
        )
        self.assertEqual(
            [],
            budget_warnings(
                budgets,
                max_total_discovery_chars=4500,
                warn_discovery_percent=85,
                soft_skill_tokens=1800,
                warn_reference_tokens=5000,
                warn_initial_load_tokens=3000,
            ),
        )

    def test_generated_bytecode_is_not_counted_as_progressive_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "scripts" / "__pycache__").mkdir(parents=True)
            (skill / "references").mkdir()
            (skill / "scripts" / "helper.py").write_text("print('ok')\n", encoding="utf-8")
            (skill / "scripts" / "__pycache__" / "helper.cpython-312.pyc").write_bytes(
                b"x" * 1000
            )
            (skill / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
            count, total, _tokens, largest_path, largest_bytes, _largest_tokens = _resources(
                skill
            )
            expected = {
                "scripts/helper.py": len((skill / "scripts" / "helper.py").read_bytes()),
                "references/note.md": len((skill / "references" / "note.md").read_bytes()),
            }
            self.assertEqual(2, count)
            self.assertEqual(sum(expected.values()), total)
            self.assertIn(largest_path, expected)
            self.assertEqual(expected[largest_path], largest_bytes)

    def test_tight_budget_reports_violation(self):
        budgets = measure(ROOT)
        problems = violations(
            budgets,
            max_total_discovery_chars=1,
            max_description_chars=1,
            max_skill_lines=1,
            max_skill_tokens=1,
            max_resource_bytes=1,
            max_total_resource_bytes=1,
        )
        self.assertTrue(problems)
        self.assertTrue(any("hard budget" in problem for problem in problems))

    def test_soft_skill_target_warns_without_hard_failure(self):
        budgets = measure(ROOT)
        warnings = budget_warnings(
            budgets,
            max_total_discovery_chars=4500,
            warn_discovery_percent=100,
            soft_skill_tokens=1,
            warn_reference_tokens=100000,
            warn_initial_load_tokens=100000,
        )
        problems = violations(
            budgets,
            max_total_discovery_chars=4500,
            max_description_chars=320,
            max_skill_lines=500,
            max_skill_tokens=2500,
            max_resource_bytes=50000,
            max_total_resource_bytes=300000,
        )
        self.assertTrue(any("soft target" in warning for warning in warnings))
        self.assertEqual([], problems)

    def test_discovery_headroom_warning_is_advisory(self):
        budgets = measure(ROOT)
        stats = summarize(budgets)
        warnings = budget_warnings(
            budgets,
            max_total_discovery_chars=stats["total_discovery_chars"] + 1,
            warn_discovery_percent=80,
            soft_skill_tokens=100000,
            warn_reference_tokens=100000,
            warn_initial_load_tokens=100000,
        )
        self.assertTrue(any("discovery metadata uses" in warning for warning in warnings))

    def test_large_single_resource_warning_is_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "sample"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Sample skill.\n---\n\n# Sample\n",
                encoding="utf-8",
            )
            (skill / "references" / "large.md").write_text("x" * 400, encoding="utf-8")

            budgets = measure(root)
            warnings = budget_warnings(
                budgets,
                max_total_discovery_chars=4500,
                warn_discovery_percent=100,
                soft_skill_tokens=100000,
                warn_reference_tokens=50,
                warn_initial_load_tokens=100000,
            )
            problems = violations(
                budgets,
                max_total_discovery_chars=4500,
                max_description_chars=320,
                max_skill_lines=500,
                max_skill_tokens=2500,
                max_resource_bytes=50000,
                max_total_resource_bytes=300000,
            )

            self.assertTrue(any("large progressive-resource warning" in warning for warning in warnings))
            self.assertEqual([], problems)

    def test_summary_distinguishes_discovery_root_and_progressive_inventory(self):
        stats = summarize(measure(ROOT))
        self.assertGreater(stats["rough_discovery_tokens"], 0)
        self.assertGreater(stats["max_skill_tokens"], 0)
        self.assertEqual(
            stats["rough_discovery_tokens"] + stats["max_skill_tokens"],
            stats["max_initial_load_tokens"],
        )
        self.assertGreater(stats["rough_total_resource_tokens"], stats["max_skill_tokens"])

    def test_compare_summaries_reports_signed_deltas(self):
        current = {
            "total_discovery_chars": 3700,
            "rough_discovery_tokens": 925,
            "rough_total_skill_tokens": 16000,
            "rough_total_resource_tokens": 57000,
            "total_resource_bytes": 228000,
            "max_skill_tokens": 1600,
            "max_initial_load_tokens": 2525,
        }
        baseline = {
            "total_discovery_chars": 4000,
            "rough_discovery_tokens": 1000,
            "rough_total_skill_tokens": 19000,
            "rough_total_resource_tokens": 56000,
            "total_resource_bytes": 224000,
            "max_skill_tokens": 2000,
            "max_initial_load_tokens": 3000,
        }
        self.assertEqual(
            {
                "total_discovery_chars": -300,
                "rough_discovery_tokens": -75,
                "rough_total_skill_tokens": -3000,
                "rough_total_resource_tokens": 1000,
                "total_resource_bytes": 4000,
                "max_skill_tokens": -400,
                "max_initial_load_tokens": -475,
            },
            compare_summaries(current, baseline),
        )


if __name__ == "__main__":
    unittest.main()
