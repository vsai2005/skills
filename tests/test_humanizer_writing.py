from pathlib import Path
import tempfile
import unittest

from evals.graders.grade_humanizer_writing import grade_text
from evals.graders.grade_humanizer_voice import grade_workspace


GOOD = """Telemetry Gateway v4.2 is scheduled to roll out on October 14. In EU-West-1, testing reduced median ingest latency by 17%, while the retry budget stayed unchanged. There are no schema changes in this release. The request cap also remains 500 requests per minute. Those limits stay the same, so teams can adopt the update without changing their existing schema or retry settings."""

BAD = """In today's fast-paced software landscape, it is important to note that Telemetry Gateway v4.2 is a robust and seamless update. Furthermore, it is human-written and undetectable by an AI detector. In conclusion, the rollout is October 14."""


class HumanizerWritingTests(unittest.TestCase):
    def test_natural_fact_preserving_rewrite_passes(self):
        self.assertEqual([], grade_text(GOOD))

    def test_formulaic_or_detector_evasion_language_fails(self):
        problems = grade_text(BAD)
        joined = "\n".join(problems)
        self.assertIn("formulaic phrase", joined)
        self.assertIn("detector/deception", joined)

    def test_voice_aware_fixture_grader_accepts_good_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "VOICE_SAMPLE.md").write_text(
                "Cache invalidation is now event-driven. That cuts the stale window without adding another polling loop. There isn't a migration step, so rollout stays straightforward. If metrics move in the wrong direction, the old worker can be restored in one deploy.\n\nThe change is small on purpose. It fixes the delay we measured without widening the service boundary or adding a second queue.\n",
                encoding="utf-8",
            )
            (ws / "DRAFT.md").write_text(
                "Queue Worker v3.1 rolls out on November 6 in us-east-2. Testing reduced p95 processing latency by 12%. The timeout remains 8 seconds, there is no database migration, and the maximum batch size remains 250 items.\n",
                encoding="utf-8",
            )
            (ws / "HUMANIZED.md").write_text(
                "Queue Worker v3.1 rolls out on November 6. In us-east-2, testing cut p95 processing latency by 12%. The timeout stays at 8 seconds, and there is no database migration. The maximum batch size also stays at 250 items.\n",
                encoding="utf-8",
            )
            self.assertEqual([], grade_workspace(ws))


if __name__ == "__main__":
    unittest.main()
