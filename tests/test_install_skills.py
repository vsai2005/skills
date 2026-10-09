from pathlib import Path
import tempfile
import unittest

from scripts.install_skills import available_skills, install


ROOT = Path(__file__).resolve().parents[1]


class InstallSkillsTests(unittest.TestCase):
    def test_discovers_expected_skills(self):
        skills = available_skills(ROOT / "skills")
        self.assertEqual(
            {"engineering-quality", "structure-feature", "debug-root-cause", "refactor-safely", "guard-architecture", "tiered-testing", "baseline-compare", "flaky-test-triage", "verify-change", "context-engineering", "source-grounded-development", "independent-review", "asd-ste100-writing", "humanizer-writing", "security-hardening"},
            set(skills),
        )

    def test_installs_selected_skill_with_references_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            installed = install(ROOT / "skills", dest, ["debug-root-cause"])
            self.assertEqual(1, len(installed))
            self.assertTrue((dest / "debug-root-cause" / "SKILL.md").is_file())
            self.assertTrue((dest / "debug-root-cause" / "references" / "root-cause-playbook.md").is_file())
            self.assertTrue((dest / "debug-root-cause" / "references" / "case-study-classifier-root-cause.md").is_file())
            self.assertTrue((dest / "debug-root-cause" / "assets" / "bug-fix-record.md").is_file())

    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            install(ROOT / "skills", dest, ["verify-change"])
            with self.assertRaises(FileExistsError):
                install(ROOT / "skills", dest, ["verify-change"])
            install(ROOT / "skills", dest, ["verify-change"], force=True)


if __name__ == "__main__":
    unittest.main()
