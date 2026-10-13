from pathlib import Path
import tempfile
import unittest

from scripts.context_pointer_audit import audit, audit_skill


ROOT = Path(__file__).resolve().parents[1]


def write_skill(root: Path, body: str) -> Path:
    skill = root / "skills" / "sample"
    (skill / "references").mkdir(parents=True)
    (skill / "assets").mkdir()
    (skill / "scripts").mkdir()
    path = skill / "SKILL.md"
    path.write_text(
        "---\nname: sample\ndescription: Sample skill with enough activation context for tests.\n---\n\n"
        + body,
        encoding="utf-8",
    )
    return path


class ContextPointerAuditTests(unittest.TestCase):
    def test_action_only_pointer_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(
                Path(tmp),
                "Use [details](references/details.md).\n",
            )
            issues, count, targets = audit_skill(path)
            self.assertEqual(1, count)
            self.assertEqual({"references/details.md"}, targets)
            self.assertTrue(any(issue.kind == "vague" for issue in issues))

    def test_conditional_or_purpose_pointer_is_not_vague(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(
                Path(tmp),
                "When ownership is unclear, use [placement rules](references/placement.md).\n"
                "For failure recovery, see [recovery guide](references/recovery.md).\n",
            )
            issues, count, _targets = audit_skill(path)
            self.assertEqual(2, count)
            self.assertFalse(any(issue.kind == "vague" for issue in issues))

    def test_duplicate_target_warns_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(
                Path(tmp),
                "For setup, use [guide](references/guide.md).\n"
                "For teardown, revisit [guide](references/guide.md).\n",
            )
            issues, _count, _targets = audit_skill(path)
            duplicates = [issue for issue in issues if issue.kind == "duplicate"]
            self.assertEqual(1, len(duplicates))
            self.assertEqual(("references/guide.md",), duplicates[0].targets)

    def test_three_link_sentence_warns_as_dense_cluster(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(
                Path(tmp),
                "For the full audit, use [a](references/a.md), "
                "[b](references/b.md), and [c](references/c.md).\n",
            )
            issues, count, _targets = audit_skill(path)
            self.assertEqual(3, count)
            self.assertTrue(any(issue.kind == "dense-cluster" for issue in issues))

    def test_audit_reports_repository_stats(self):
        issues, stats = audit(ROOT)
        self.assertEqual(17, stats.skills)
        self.assertGreater(stats.pointers, 0)
        self.assertGreater(stats.unique_targets, 0)
        self.assertEqual(
            stats.vague_pointers,
            sum(issue.kind == "vague" for issue in issues),
        )


if __name__ == "__main__":
    unittest.main()
