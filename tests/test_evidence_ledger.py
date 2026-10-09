from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.evidence_ledger import (
    RepoSnapshot,
    append_event,
    current_states,
    load_events,
    main,
    render_report,
    repository_snapshot,
)


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.com"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "app.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "base"], check=True)


class EvidenceLedgerTests(unittest.TestCase):
    def test_report_separates_verified_and_not_verified(self):
        snapshot = RepoSnapshot("/tmp/repo", "abc", "state")
        events = [
            {"event": "plan", "id": "EV-1", "label": "Unit tests", "command": "pytest", "timestamp": "2026-01-01T00:00:00Z"},
            {"event": "run", "id": "EV-1", "label": "Unit tests", "command": "pytest", "exit_code": 0, "timestamp": "2026-01-01T00:01:00Z", "repo_root": "/tmp/repo", "git_head": "abc", "state_fingerprint": "state"},
            {"event": "plan", "id": "EV-2", "label": "E2E", "command": "npm run e2e", "timestamp": "2026-01-01T00:02:00Z"},
            {"event": "record", "id": "EV-3", "label": "Build", "command": "npm run build", "exit_code": 0, "timestamp": "2026-01-01T00:03:00Z", "repo_root": "/tmp/repo", "git_head": "abc", "state_fingerprint": "state"},
        ]
        report = render_report(current_states(events, snapshot))
        self.assertIn("## Verified", report)
        self.assertIn("Unit tests", report)
        self.assertIn("## Not verified", report)
        self.assertIn("planned but not run", report)
        self.assertIn("externally recorded exit 0", report)

    def test_jsonl_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.jsonl"
            append_event(path, {"event": "plan", "id": "EV-1", "label": "Compile", "command": f"{sys.executable} -m compileall .", "timestamp": "2026-01-01T00:00:00Z"})
            events = load_events(path)
            self.assertEqual(1, len(events))
            self.assertEqual("EV-1", events[0]["id"])

    def test_run_records_exit_code_timestamp_and_repo_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            code = main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-1", "--label", "Smoke", "--", sys.executable, "-c", "raise SystemExit(0)"])
            self.assertEqual(0, code)
            events = load_events(ledger)
            self.assertEqual(0, events[0]["exit_code"])
            self.assertTrue(str(events[0]["timestamp"]).endswith("Z"))
            self.assertEqual(str(root.resolve()), events[0]["repo_root"])
            self.assertTrue(events[0]["state_fingerprint"])

    def test_success_becomes_stale_after_repository_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            self.assertEqual(0, main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-1", "--label", "Tests", "--", sys.executable, "-c", "pass"]))
            before = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("verified", before.status)
            (root / "app.txt").write_text("changed after verification\n", encoding="utf-8")
            after = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("stale", after.status)
            self.assertIn("rerun required", render_report([after]))

    def test_recorded_external_success_is_not_locally_verified(self):
        events = [{"event": "record", "id": "EV-X", "label": "CI", "command": "pytest", "exit_code": 0, "timestamp": "2026-01-01T00:00:00Z"}]
        state = current_states(events)[0]
        self.assertEqual("external", state.status)

    def test_report_includes_pending_tests(self):
        class Pending:
            id = "PT-1"
            command = "npm run e2e"
            trigger = "before merge"

        report = render_report([], [Pending()])
        self.assertIn("Pending test PT-1", report)
        self.assertNotIn("## Not verified\n- None.", report)

    def test_json_report_command_does_not_need_memory_reconstruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "evidence.jsonl"
            append_event(ledger, {"event": "plan", "id": "EV-1", "label": "E2E", "command": "e2e", "timestamp": "2026-01-01T00:00:00Z"})
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, main(["--ledger", str(ledger), "--repo", tmp, "report", "--pending-tests", str(Path(tmp) / "none.md")]))
            self.assertIn("planned but not run", output.getvalue())

    def test_invalid_event_type_is_rejected_during_state_build(self):
        with self.assertRaises(ValueError):
            current_states([{"event": "unknown", "id": "EV-X", "timestamp": "2026-01-01T00:00:00Z"}])

    def test_planned_command_cannot_be_replaced_under_same_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            planned = f"{sys.executable} -c pass"
            self.assertEqual(0, main(["--ledger", str(ledger), "--repo", str(root), "plan", "--id", "EV-LOCK", "--label", "Tests", "--command", planned]))
            code = main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-LOCK", "--label", "Tests", "--", sys.executable, "-c", "print('different')"])
            self.assertEqual(2, code)
            self.assertEqual(1, len(load_events(ledger)))

    def test_success_that_mutates_repository_is_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            code = "from pathlib import Path; Path('app.txt').write_text('changed\\n')"
            self.assertEqual(0, main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-MUT", "--label", "Mutation", "--", sys.executable, "-c", code]))
            state = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("mutated", state.status)
            self.assertIn("changed repository state", render_report([state]))

    def test_explicit_state_change_can_be_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            code = "from pathlib import Path; Path('app.txt').write_text('generated\\n')"
            self.assertEqual(0, main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-GEN", "--label", "Generator", "--allow-state-change", "--", sys.executable, "-c", code]))
            state = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("verified", state.status)

    def test_success_outside_git_is_unbound_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "evidence.jsonl"
            self.assertEqual(0, main(["--ledger", str(ledger), "--repo", str(root), "run", "--id", "EV-UNBOUND", "--label", "Smoke", "--", sys.executable, "-c", "pass"]))
            state = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("unbound", state.status)
            self.assertIn("not bound to a Git repository state", render_report([state]))

    def test_historical_command_identity_change_is_rejected(self):
        events = [
            {"event": "plan", "id": "EV-X", "label": "Tests", "command": "pytest", "timestamp": "2026-01-01T00:00:00Z"},
            {"event": "run", "id": "EV-X", "label": "Tests", "command": "true", "exit_code": 0, "timestamp": "2026-01-01T00:01:00Z"},
        ]
        with self.assertRaisesRegex(ValueError, "command identity changed"):
            current_states(events)


if __name__ == "__main__":
    unittest.main()
