from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.openai_metadata_check import check_skill, refresh_skill


ROOT = Path(__file__).resolve().parents[1]


class OpenAiMetadataCheckTests(unittest.TestCase):
    def test_current_metadata_hashes_match_descriptions(self):
        problems = []
        for skill_dir in (ROOT / "skills").iterdir():
            if (skill_dir / "SKILL.md").is_file():
                problem = check_skill(skill_dir)
                if problem:
                    problems.append(problem)
        self.assertEqual([], problems)

    def test_description_change_marks_metadata_stale_until_refreshed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = ROOT / "skills" / "debug-root-cause"
            skill_dir = Path(tmp) / "debug-root-cause"
            shutil.copytree(source, skill_dir)
            skill_md = skill_dir / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            text = text.replace(
                "description:",
                "description:",
                1,
            ).replace(
                "Fix reproducible bugs, regressions, crashes, wrong outputs, or stable failing tests",
                "Fix reproducible bugs, regressions, crashes, wrong outputs, or deterministic stable failing tests",
                1,
            )
            skill_md.write_text(text, encoding="utf-8")
            self.assertIn("stale", check_skill(skill_dir))
            refresh_skill(skill_dir)
            self.assertIsNone(check_skill(skill_dir))


if __name__ == "__main__":
    unittest.main()
