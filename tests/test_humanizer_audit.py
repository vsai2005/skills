import tempfile
import unittest
from pathlib import Path

from scripts.humanizer_audit import audit_text, compare_texts, protected_literals


class HumanizerAuditTests(unittest.TestCase):
    def test_formulaic_text_triggers_audit_signals(self):
        text = (
            "In today's fast-paced software landscape, it is important to note that the platform is robust. "
            "Furthermore, the service is seamless. Furthermore, the workflow is powerful. "
            "Furthermore, the process is comprehensive."
        )
        result = audit_text(text)
        codes = {item["code"] for item in result["signals"]}
        self.assertIn("generic_opener", codes)
        self.assertIn("formulaic_transitions", codes)
        self.assertFalse(result["already_good"])

    def test_natural_text_can_hit_already_good_stop_condition(self):
        text = (
            "The deploy finished at 14:20. The API stayed available during the rollout, and error rates did not move. "
            "We will keep the old worker pool for one day so rollback stays simple if traffic changes overnight."
        )
        result = audit_text(text)
        self.assertTrue(result["already_good"])

    def test_compare_detects_missing_literals_modality_and_negation(self):
        source = "Telemetry v4.2 may fail after 30 seconds. Do not exceed 500 requests per minute. See `retry_budget`."
        rewrite = "Telemetry can fail after a short wait. Exceed the request limit only when necessary."
        result = compare_texts(source, rewrite)
        self.assertIn("v4.2", result["missing_literals"])
        self.assertIn("30", result["missing_literals"])
        self.assertIn("500", result["missing_literals"])
        self.assertIn("`retry_budget`", result["missing_literals"])
        self.assertIn("may", result["missing_modals"])
        self.assertIn("not", result["missing_negations"])
        self.assertFalse(result["integrity_ok"])

    def test_compare_accepts_preserved_literals_and_modal(self):
        source = "Telemetry v4.2 may fail after 30 seconds. Do not exceed 500 requests per minute."
        rewrite = "After 30 seconds, Telemetry v4.2 may fail. Do not send more than 500 requests per minute."
        result = compare_texts(source, rewrite)
        self.assertEqual([], result["missing_literals"])
        self.assertEqual({}, result["missing_modals"])
        self.assertEqual({}, result["missing_negations"])
        self.assertTrue(result["integrity_ok"])

    def test_protected_literals_include_code_numbers_and_codes(self):
        literals = protected_literals("Use `npm test` after 17% at E104 and https://example.com/docs.")
        self.assertIn("`npm test`", literals)
        self.assertIn("17%", literals)
        self.assertIn("E104", literals)
        self.assertIn("https://example.com/docs.", literals)


if __name__ == "__main__":
    unittest.main()
