import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.evidence_ledger import main as evidence_main
from scripts.pending_tests import add_item, complete_item, load_items, render, write_items


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.com"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "app.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "base"], check=True)


class PendingTestsTests(unittest.TestCase):
    def test_complete_requires_evidence_or_superseding_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PENDING_TESTS.md"
            with patch("scripts.pending_tests.uuid.uuid4") as fake_uuid:
                fake_uuid.return_value.hex = "12345678abcdef00"
                item = add_item(path, "pytest tests/e2e", "heavy suite", "before merge")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                complete_item(path, item.id)

    def test_add_and_complete_with_current_executed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            path = root / "PENDING_TESTS.md"
            ledger = root / ".verification" / "evidence.jsonl"
            with patch("scripts.pending_tests.uuid.uuid4") as fake_uuid:
                fake_uuid.return_value.hex = "12345678abcdef00"
                command = f"{sys.executable} -c pass"
            item = add_item(path, command, "heavy suite", "before merge")
            self.assertEqual(
                0,
                evidence_main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-OK", "--label", "E2E", "--", sys.executable, "-c", "pass"]),
            )
            completed = complete_item(path, item.id, evidence_id="EV-OK", ledger=ledger, repo=root)
            self.assertEqual(item, completed)
            self.assertEqual([], load_items(path))
            self.assertIn("No pending tests.", path.read_text(encoding="utf-8"))

    def test_stale_evidence_cannot_complete_pending_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            path = root / "PENDING_TESTS.md"
            ledger = root / ".verification" / "evidence.jsonl"
            item = add_item(path, "pytest", "heavy", "before merge")
            self.assertEqual(0, evidence_main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-OLD", "--label", "Tests", "--", sys.executable, "-c", "pass"]))
            (root / "app.txt").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not current verified"):
                complete_item(path, item.id, evidence_id="EV-OLD", ledger=ledger, repo=root)


    def test_different_evidence_command_cannot_complete_pending_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            path = root / "PENDING_TESTS.md"
            ledger = root / ".verification" / "evidence.jsonl"
            item = add_item(path, "npm run e2e", "heavy", "before merge")
            self.assertEqual(0, evidence_main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-OTHER", "--label", "Unit", "--", sys.executable, "-c", "pass"]))
            with self.assertRaisesRegex(ValueError, "different command"):
                complete_item(path, item.id, evidence_id="EV-OTHER", ledger=ledger, repo=root)

    def test_explicit_superseding_reason_can_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PENDING_TESTS.md"
            item = add_item(path, "old command", "old environment", "before merge")
            completed = complete_item(path, item.id, superseded_by="Replaced by equivalent new browser matrix command")
            self.assertEqual(item.id, completed.id)

    def test_requires_reason_and_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PENDING_TESTS.md"
            with self.assertRaises(ValueError):
                add_item(path, "pytest", "", "before merge")

    def test_render_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PENDING_TESTS.md"
            write_items(path, [])
            self.assertEqual([], load_items(path))
            self.assertIn("Managed by", render([]))

    def test_completion_can_append_local_audit_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "PENDING_TESTS.md"
            history = root / ".verification" / "pending_tests_history.jsonl"
            item = add_item(path, "old command", "old environment", "before merge")
            complete_item(path, item.id, superseded_by="Replaced by equivalent browser matrix", history=history)
            events = [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(1, len(events))
            self.assertEqual(item.id, events[0]["pending_test"]["id"])
            self.assertEqual("completed", events[0]["event"])


if __name__ == "__main__":
    unittest.main()
