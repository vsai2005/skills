import json
from pathlib import Path
import tempfile
import unittest

from scripts.invocation_classification import discovery_budgets, load_policy, report, validate_policy


ROOT = Path(__file__).resolve().parents[1]


class InvocationClassificationTests(unittest.TestCase):
    def test_current_policy_covers_every_skill_once_without_enforcement(self):
        policy = load_policy(ROOT / "evals" / "invocation-policy.json")
        self.assertFalse(policy["enforced"])
        self.assertEqual([], validate_policy(ROOT, policy))
        result = report(ROOT, policy)
        self.assertEqual(17, result["skills"])
        self.assertEqual(
            17,
            sum(result["classification_counts"].values()),
        )

    def test_report_is_hypothetical_and_reduces_only_explicit_candidates(self):
        policy = load_policy(ROOT / "evals" / "invocation-policy.json")
        result = report(ROOT, policy)
        discovery = result["discovery"]
        self.assertGreater(discovery["explicit_candidate_chars"], 0)
        self.assertLess(
            discovery["hypothetical_model_visible_chars"],
            discovery["current_chars"],
        )
        self.assertIn("Hypothetical", result["claim_boundary"])
        self.assertFalse(result["enforced"])

    def test_discovery_measurement_does_not_scan_progressive_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "sample"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Focused sample skill for discovery measurement.\n---\n\n# Sample\n",
                encoding="utf-8",
            )
            (skill / "references" / "binary.bin").write_bytes(b"\xff" * 10000)
            budgets = discovery_budgets(root)
            self.assertEqual(
                len("sample") + len("Focused sample skill for discovery measurement."),
                budgets["sample"],
            )

    def test_duplicate_classification_is_rejected(self):
        policy = load_policy(ROOT / "evals" / "invocation-policy.json")
        policy = json.loads(json.dumps(policy))
        duplicate = policy["classes"]["model-default"][0]
        policy["classes"]["explicit-candidate"].append(duplicate)
        problems = validate_policy(ROOT, policy)
        self.assertTrue(any("classified more than once" in problem for problem in problems))

    def test_policy_cannot_turn_enforcement_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            data = json.loads((ROOT / "evals" / "invocation-policy.json").read_text(encoding="utf-8"))
            data["enforced"] = True
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-enforced"):
                load_policy(path)


if __name__ == "__main__":
    unittest.main()
