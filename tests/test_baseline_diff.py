from pathlib import Path
import json
import tempfile
import unittest

from scripts.baseline_diff import FailureRecord, compare_failures, load_failures, summary


class BaselineDiffTests(unittest.TestCase):
    def test_classifies_matching_signature_as_pre_existing_and_new_id_as_regression(self):
        baseline = [FailureRecord("test.alpha", "alpha broke"), FailureRecord("test.beta", "same")]
        current = [FailureRecord("test.beta", "same", "still broken"), FailureRecord("test.gamma", "new")]
        classified, resolved = compare_failures(baseline, current)
        self.assertEqual(["pre-existing", "regression"], [item.classification for item in classified])
        self.assertEqual(["test.alpha"], [item.key for item in resolved])
        self.assertEqual(1, summary(classified, resolved)["regressions"])

    def test_same_id_with_changed_signature_is_regression(self):
        baseline = [FailureRecord("test.auth", "expected 403 got 500")]
        current = [FailureRecord("test.auth", "expected 403 got 200")]
        classified, _ = compare_failures(baseline, current)
        self.assertEqual("regression", classified[0].classification)
        self.assertEqual("same-id-signature-changed", classified[0].reason)

    def test_loads_text_and_json_inventories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_path = root / "failures.txt"
            text_path.write_text("# comment\ntest.alpha\tmessage\ntest.beta\n", encoding="utf-8")
            json_path = root / "failures.json"
            json_path.write_text(json.dumps(["test.alpha", {"id": "test.gamma", "signature": "boom", "detail": "detail"}]), encoding="utf-8")
            text_items = load_failures(text_path)
            json_items = load_failures(json_path)
            self.assertEqual(["test.alpha", "test.beta"], [item.key for item in text_items])
            self.assertEqual("message", text_items[0].signature)
            self.assertEqual(["test.alpha", "test.gamma"], [item.key for item in json_items])
            self.assertEqual("boom", json_items[1].signature)

    def test_null_failure_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failures.json"
            path.write_text(json.dumps([{"id": None, "detail": "boom"}]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "null failure id"):
                load_failures(path)

    def test_junit_xml_failure_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "junit.xml"
            path.write_text(
                '<testsuite><testcase classname="Auth" name="forbidden"><failure message="expected 403">got 200</failure></testcase><testcase classname="Auth" name="allowed" /></testsuite>',
                encoding="utf-8",
            )
            items = load_failures(path)
            self.assertEqual(1, len(items))
            self.assertEqual("Auth::forbidden", items[0].key)
            self.assertIn("expected 403", items[0].signature)

    def test_duplicate_failure_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failures.txt"
            path.write_text("same\nsame\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_failures(path)

    def test_junit_identity_uses_file_to_disambiguate_same_class_and_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "junit.xml"
            path.write_text(
                '<testsuites><testsuite name="a"><testcase file="a/test_auth.py" classname="Auth" name="denied"><failure message="A" /></testcase></testsuite><testsuite name="b"><testcase file="b/test_auth.py" classname="Auth" name="denied"><failure message="B" /></testcase></testsuite></testsuites>',
                encoding="utf-8",
            )
            items = load_failures(path)
            self.assertEqual(["a/test_auth.py::Auth::denied", "b/test_auth.py::Auth::denied"], [item.key for item in items])

    def test_junit_identity_uses_suite_when_no_file_or_package_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "junit.xml"
            path.write_text(
                '<testsuites><testsuite name="module-a"><testcase classname="Auth" name="denied"><failure message="A" /></testcase></testsuite><testsuite name="module-b"><testcase classname="Auth" name="denied"><failure message="B" /></testcase></testsuite></testsuites>',
                encoding="utf-8",
            )
            items = load_failures(path)
            self.assertEqual(["module-a::Auth::denied", "module-b::Auth::denied"], [item.key for item in items])


if __name__ == "__main__":
    unittest.main()
