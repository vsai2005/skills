from pathlib import Path
import json
import tempfile
import unittest

from scripts.export_standard_evals import export_cases


ROOT = Path(__file__).resolve().parents[1]


class StandardEvalExportTests(unittest.TestCase):
    def test_exports_one_file_per_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = export_cases(ROOT, Path(tmp) / "out")
            self.assertEqual(17, len(written))
            for path in written:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("skill_name", data)
                self.assertTrue(data["evals"])
                for case in data["evals"]:
                    self.assertTrue(case["prompt"])
                    self.assertTrue(case["expected_output"])
                    self.assertIsInstance(case["assertions"], list)
                    self.assertTrue(case["assertions"])
                    self.assertIn("source_case_id", case)

    def test_project_orchestrator_export_is_traceable(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            export_cases(ROOT, out)
            path = out / "project-quality-orchestrator" / "evals" / "evals.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            source_ids = {case["source_case_id"] for case in data["evals"]}
            self.assertIn("project-quality-cross-layer", source_ids)


if __name__ == "__main__":
    unittest.main()
