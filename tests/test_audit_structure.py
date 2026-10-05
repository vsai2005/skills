from pathlib import Path
import tempfile
import unittest

from scripts.audit_structure import audit, should_fail


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "audit_structure"


class AuditStructureTests(unittest.TestCase):
    def test_detects_skipped_test_and_type_suppression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "example.ts").write_text((FIXTURES / "suppressions.txt").read_text(encoding="utf-8"), encoding="utf-8")
            (root / "tests" / "example.test.ts").write_text((FIXTURES / "skipped-test.txt").read_text(encoding="utf-8"), encoding="utf-8")
            findings = audit(root)
            codes = {f.code for f in findings}
            self.assertIn("type-suppression", codes)
            self.assertIn("typescript-any", codes)
            self.assertIn("skipped-test", codes)
            self.assertIn("debug-log", codes)
            self.assertIn("debugger", codes)
            self.assertTrue(should_fail(findings, "high"))

    def test_large_handwritten_source_is_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            src.mkdir()
            (src / "giant.py").write_text("x = 1\n" * 801, encoding="utf-8")
            findings = audit(root)
            self.assertTrue(any(f.code == "large-file" and f.severity == "HIGH" for f in findings))

    def test_exclude_glob_skips_intentional_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            (tests / "fixture.test.ts").write_text((FIXTURES / "skipped-test.txt").read_text(encoding="utf-8"), encoding="utf-8")
            findings = audit(root, ("tests/**",))
            self.assertEqual([], findings)

    def test_generated_file_avoids_large_file_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "generated"
            generated.mkdir()
            (generated / "client.ts").write_text("export const x = 1;\n" * 2000, encoding="utf-8")
            findings = audit(root)
            self.assertFalse(any(f.code == "large-file" for f in findings))

    def test_missing_root_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            with self.assertRaises(FileNotFoundError):
                audit(missing)

    def test_scans_additional_source_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.dart").write_text((FIXTURES / "dart-marker.txt").read_text(encoding="utf-8"), encoding="utf-8")
            findings = audit(root)
            self.assertTrue(any(f.path == "app.dart" and f.code == "".join(("to", "do-", "fix", "me")) for f in findings))


if __name__ == "__main__":
    unittest.main()
