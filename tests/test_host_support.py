from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HostSupportTests(unittest.TestCase):
    def test_host_matrix_has_expected_surfaces_and_honest_evidence_flags(self):
        data = json.loads((ROOT / "compatibility" / "hosts.json").read_text(encoding="utf-8"))
        self.assertEqual(1, data["schema_version"])
        hosts = {item["id"]: item for item in data["hosts"]}
        self.assertEqual(
            {"openai-codex", "claude-code", "google-antigravity", "github-copilot"},
            set(hosts),
        )
        for name in ("openai-codex", "claude-code", "google-antigravity"):
            self.assertTrue(hosts[name]["activation_adapter"])
            self.assertTrue(hosts[name]["behavior_adapter"])
            self.assertFalse(hosts[name]["published_empirical_claims"])
        self.assertEqual("documented-compatible", hosts["github-copilot"]["structural_support"])
        self.assertFalse(hosts["github-copilot"]["activation_adapter"])
        self.assertFalse(hosts["github-copilot"]["published_empirical_claims"])


if __name__ == "__main__":
    unittest.main()
