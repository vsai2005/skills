from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from scripts.evidence_freshness import load_registry, validate_claims
from scripts.eval_provenance import sha256_tree


ROOT = Path(__file__).resolve().parents[1]


class EvidenceFreshnessTests(unittest.TestCase):
    def test_empty_registry_is_valid(self):
        registry = load_registry(ROOT / "evidence" / "registry.json")
        self.assertEqual([], validate_claims(ROOT, registry))

    def test_skill_hash_change_marks_claim_stale(self):
        now = datetime(2026, 10, 12, tzinfo=timezone.utc)
        registry = {
            "schema_version": 1,
            "max_age_days": 90,
            "claims": [
                {
                    "id": "x",
                    "skill": "debug-root-cause",
                    "host": "codex",
                    "model": "model-x",
                    "status": "BENEFICIAL",
                    "tested_at": "2026-10-11T00:00:00Z",
                    "skill_sha256": "0" * 64,
                    "paired_runs": 5,
                }
            ],
        }
        problems = validate_claims(ROOT, registry, now=now)
        self.assertTrue(any("skill hash" in problem for problem in problems))

    def test_old_claim_expires(self):
        now = datetime(2026, 10, 12, tzinfo=timezone.utc)
        skill = "debug-root-cause"
        registry = {
            "schema_version": 1,
            "max_age_days": 30,
            "claims": [
                {
                    "id": "x",
                    "skill": skill,
                    "host": "codex",
                    "model": "model-x",
                    "status": "NEUTRAL",
                    "tested_at": "2026-01-01T00:00:00Z",
                    "skill_sha256": sha256_tree(ROOT / "skills" / skill),
                    "paired_runs": 5,
                }
            ],
        }
        problems = validate_claims(ROOT, registry, now=now)
        self.assertTrue(any("days old" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
