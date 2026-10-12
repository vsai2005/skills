from pathlib import Path
import json
import tempfile
import unittest

from scripts.eval_provenance import sha256_tree
from scripts.publish_evidence import publish, sanitize_claims


ROOT = Path(__file__).resolve().parents[1]


class PublishEvidenceTests(unittest.TestCase):
    def _entry(self, skill: str = "debug-root-cause") -> dict:
        return {
            "provider": "codex",
            "model": "model-x",
            "skill": skill,
            "skill_sha256": sha256_tree(ROOT / "skills" / skill),
            "pairs": 5,
            "campaigns": ["c1"],
            "classification": "BENEFICIAL",
            "strong_evidence": True,
            "freshness": "current",
            "score_delta": 0.2,
            "bootstrap_ci": [0.1, 0.3],
            "confidence": 0.95,
            "token_ratio": 1.1,
            "time_ratio": 1.2,
        }

    def test_sanitizes_only_strong_current_entries(self):
        source = {
            "schema_version": 2,
            "entries": [
                self._entry(),
                {**self._entry("verify-change"), "strong_evidence": False},
            ],
        }
        claims = sanitize_claims(ROOT, source, "2026-10-12T00:00:00Z")
        self.assertEqual(1, len(claims))
        claim = claims[0]
        self.assertEqual("debug-root-cause", claim["skill"])
        self.assertEqual("codex", claim["host"])
        self.assertNotIn("prompt", claim)
        self.assertNotIn("trace", claim)

    def test_rejects_provider_default_model(self):
        entry = self._entry()
        entry["model"] = "provider-default"
        source = {"schema_version": 2, "entries": [entry]}
        with self.assertRaisesRegex(ValueError, "explicit model"):
            sanitize_claims(ROOT, source, "2026-10-12T00:00:00Z")

    def test_publish_writes_fresh_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "strong.json"
            output_path = Path(tmp) / "registry.json"
            source_path.write_text(
                json.dumps({"schema_version": 2, "entries": [self._entry()]}),
                encoding="utf-8",
            )
            registry = publish(
                ROOT,
                source_path,
                output_path,
                "2026-10-12T00:00:00+00:00",
                replace=True,
            )
            self.assertEqual(1, len(registry["claims"]))
            stored = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("BENEFICIAL", stored["claims"][0]["status"])


if __name__ == "__main__":
    unittest.main()
