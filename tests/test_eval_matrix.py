from pathlib import Path
import json
import tempfile
import unittest

from scripts.eval_matrix import build_matrix, load_cases


ROOT = Path(__file__).resolve().parents[1]


class EvalMatrixTests(unittest.TestCase):
    def test_builds_control_and_treatment_for_each_repetition(self):
        cases = [{"id": "x", "skills": ["debug-root-cause"], "fixture": "repo", "request": "fix it", "expected_behaviors": ["a", "b"]}]
        matrix = build_matrix(cases, 2)
        self.assertEqual(4, len(matrix))
        self.assertEqual(["control", "treatment", "control", "treatment"], [item["mode"] for item in matrix])
        self.assertIsNone(matrix[0]["skill"])
        self.assertEqual("debug-root-cause", matrix[1]["skill"])

    def test_real_behavior_cases_load(self):
        cases = load_cases(ROOT / "evals" / "behavior-cases.json")
        self.assertGreaterEqual(len(cases), 10)

    def test_rejects_zero_runs(self):
        with self.assertRaises(ValueError):
            build_matrix([{"id": "x", "skills": ["a"], "request": "r"}], 0)

    def test_rejects_invalid_cases_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            path.write_text(json.dumps([{"id": "x", "request": "r", "skills": []}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cases(path)


if __name__ == "__main__":
    unittest.main()
