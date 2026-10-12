from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)


def description(name: str) -> str:
    text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError(f"missing frontmatter for {name}")
    for line in match.group(1).splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"missing description for {name}")


class ActivationMetadataTests(unittest.TestCase):
    def test_orchestration_boundaries_remain_explicit(self):
        engineering = description("engineering-quality")
        project = description("project-quality-orchestrator")
        verify = description("verify-change")
        review = description("independent-review")

        self.assertIn("multiple engineering modes", engineering)
        self.assertIn("project-quality-orchestrator", engineering)

        self.assertIn("cross-layer audits", project)
        self.assertIn("canonical source", project)
        self.assertIn("final consumed output", project)
        self.assertIn("ordinary final-diff", project)

        self.assertIn("final or pre-merge", verify)
        self.assertIn("completed software change", verify)
        self.assertIn("Not for a broad source-to-consumer audit", verify)

        self.assertIn("fresh-context second review", review)
        self.assertIn("not for an ordinary readiness check", review)

    def test_discovery_descriptions_stay_compact(self):
        for skill_dir in (ROOT / "skills").iterdir():
            if (skill_dir / "SKILL.md").is_file():
                self.assertLessEqual(len(description(skill_dir.name)), 320, skill_dir.name)


if __name__ == "__main__":
    unittest.main()
