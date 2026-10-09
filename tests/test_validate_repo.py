from pathlib import Path
import json
import shutil
import tempfile
import unittest

from scripts.generate_manifest import build_manifest
from scripts.validate_repo import parse_minimal_frontmatter, validate_repo


ROOT = Path(__file__).resolve().parents[1]


def copy_repo(tmp: str) -> Path:
    dest = Path(tmp) / "repo"
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


def refresh_manifest(root: Path) -> None:
    (root / "FILE_MANIFEST.txt").write_text(build_manifest(root), encoding="utf-8")


class ValidateRepoTests(unittest.TestCase):
    def test_repository_is_valid(self):
        problems = validate_repo(ROOT)
        errors = [p for p in problems if p.level == "ERROR"]
        self.assertEqual([], errors, "\n".join(p.render(ROOT) for p in errors))

    def test_frontmatter_rejects_empty_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("---\nname: demo\ndescription:\n---\nBody\n", encoding="utf-8")
            data, problems = parse_minimal_frontmatter(path)
            self.assertIsNotNone(data)
            self.assertTrue(any("empty" in p.message for p in problems))

    def test_frontmatter_rejects_extra_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(
                "---\nname: demo\ndescription: A sufficiently descriptive trigger for testing.\nversion: 1.0.0\n---\nBody\n",
                encoding="utf-8",
            )
            _, problems = parse_minimal_frontmatter(path)
            self.assertTrue(any("unsupported" in p.message for p in problems))

    def test_invalid_activation_eval_json_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / "evals" / "activation-cases.json").write_text("{not-json", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and "activation-cases.json" in str(p.path) and "invalid JSON" in p.message for p in problems))

    def test_version_mismatch_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and "does not match VERSION" in p.message for p in problems))

    def test_missing_codex_skills_field_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            path = root / ".codex-plugin" / "plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data.pop("skills", None)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and p.path == path and "skills directory" in p.message for p in problems))

    def test_orphan_skill_resource_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            orphan = root / "skills" / "structure-feature" / "references" / "orphan.md"
            orphan.write_text("# Orphan\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "WARN" and p.path == orphan and "not reachable" in p.message for p in problems))

    def test_stale_file_manifest_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / "README.md").write_text((root / "README.md").read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and p.path.name == "FILE_MANIFEST.txt" and ("mismatch" in p.message or "missing release file" in p.message) for p in problems))

    def test_invalid_live_eval_fixture_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            path = root / "evals" / "live-cases.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data[0]["fixture"] = "evals/live-fixtures/does-not-exist"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and p.path == path and "invalid live evals" in p.message for p in problems))

    def test_invalid_benchmark_policy_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            path = root / "evals" / "benchmark-policy.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["confidence"] = 2.0
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and p.path == path and "benchmark policy" in p.message for p in problems))

    def test_live_eval_coverage_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            path = root / "evals" / "live-cases.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data = [case for case in data if case.get("skill") != "flaky-test-triage"]
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            refresh_manifest(root)
            problems = validate_repo(root)
            self.assertTrue(any(p.level == "ERROR" and p.path == path and "live evals do not cover" in p.message for p in problems))


if __name__ == "__main__":
    unittest.main()
