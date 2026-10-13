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

    def test_capture_output_retains_full_log_but_prints_compact_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            visible = StringIO()
            with redirect_stdout(visible):
                code = main([
                    "--ledger", str(ledger),
                    "--repo", str(root),
                    "run",
                    "--id", "EV-CAP",
                    "--label", "Noisy tests",
                    "--capture-output",
                    "--",
                    sys.executable,
                    "-c",
                    "print('x' * 20000)",
                ])
            self.assertEqual(0, code)
            summary = visible.getvalue()
            self.assertLess(len(summary), 1000)
            self.assertIn("EV-CAP Noisy tests: exit 0", summary)
            self.assertNotIn("x" * 100, summary)

            event = load_events(ledger)[-1]
            stdout_meta = event["stdout_artifact"]
            artifact = Path(stdout_meta["path"])
            self.assertTrue(artifact.is_file())
            artifact_bytes = artifact.read_bytes()
            self.assertGreaterEqual(len(artifact_bytes), 20000)
            self.assertEqual(len(artifact_bytes), stdout_meta["bytes"])

            state = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("verified", state.status)
            self.assertIn("[EV-CAP]", render_report([state]))

    def test_view_reads_only_requested_retained_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    0,
                    main([
                        "--ledger", str(ledger),
                        "--repo", str(root),
                        "run",
                        "--id", "EV-VIEW",
                        "--label", "Many lines",
                        "--capture-output",
                        "--",
                        sys.executable,
                        "-c",
                        "for i in range(1, 301): print(f'line-{i:03d}')",
                    ]),
                )

            visible = StringIO()
            with redirect_stdout(visible):
                self.assertEqual(
                    0,
                    main([
                        "--ledger", str(ledger),
                        "--repo", str(root),
                        "view",
                        "--id", "EV-VIEW",
                        "--stream", "stdout",
                        "--start-line", "101",
                        "--line-count", "3",
                    ]),
                )
            viewed = visible.getvalue()
            self.assertIn("lines 101-103 of 300", viewed)
            self.assertIn("line-101", viewed)
            self.assertIn("line-103", viewed)
            self.assertNotIn("line-100", viewed)
            self.assertNotIn("line-104", viewed)

    def test_failed_capture_keeps_full_stderr_for_bounded_drilldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            visible = StringIO()
            with redirect_stdout(visible):
                code = main([
                    "--ledger", str(ledger),
                    "--repo", str(root),
                    "run",
                    "--id", "EV-FAIL",
                    "--label", "Failing check",
                    "--capture-output",
                    "--",
                    sys.executable,
                    "-c",
                    "import sys; print('needle-error', file=sys.stderr); raise SystemExit(7)",
                ])
            self.assertEqual(7, code)
            self.assertIn("failure excerpt:", visible.getvalue())
            self.assertIn("needle-error", visible.getvalue())
            self.assertLess(len(visible.getvalue()), 2500)

            drill = StringIO()
            with redirect_stdout(drill):
                self.assertEqual(
                    0,
                    main([
                        "--ledger", str(ledger),
                        "--repo", str(root),
                        "view",
                        "--id", "EV-FAIL",
                        "--stream", "stderr",
                        "--tail", "5",
                    ]),
                )
            self.assertIn("needle-error", drill.getvalue())

    def test_capture_rejects_path_traversal_evidence_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            code = main([
                "--ledger", str(ledger),
                "--repo", str(root),
                "run",
                "--id", "../escape",
                "--label", "Unsafe id",
                "--capture-output",
                "--",
                sys.executable,
                "-c",
                "print('should not run')",
            ])
            self.assertEqual(2, code)
            self.assertFalse((root / "escape").exists())
            self.assertEqual([], load_events(ledger))

    def test_view_rejects_tampered_artifact_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    0,
                    main([
                        "--ledger", str(ledger),
                        "--repo", str(root),
                        "run",
                        "--id", "EV-TAMPER",
                        "--label", "Captured",
                        "--capture-output",
                        "--",
                        sys.executable,
                        "-c",
                        "print('original')",
                    ]),
                )
            event = load_events(ledger)[-1]
            Path(event["stdout_artifact"]["path"]).write_text("tampered\n", encoding="utf-8")
            self.assertEqual(
                2,
                main([
                    "--ledger", str(ledger),
                    "--repo", str(root),
                    "view",
                    "--id", "EV-TAMPER",
                    "--stream", "stdout",
                    "--tail", "5",
                ]),
            )

    def test_view_rejects_artifact_path_outside_allowed_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            outside = root / "app.txt"
            append_event(
                ledger,
                {
                    "event": "run",
                    "id": "EV-ESCAPE",
                    "label": "Crafted",
                    "command": "pytest",
                    "exit_code": 0,
                    "timestamp": "2026-01-01T00:00:00Z",
                    "capture_output": True,
                    "stdout_artifact": {
                        "path": str(outside),
                        "sha256": "0" * 64,
                        "bytes": outside.stat().st_size,
                        "lines": 1,
                    },
                    "stderr_artifact": {
                        "path": str(outside),
                        "sha256": "0" * 64,
                        "bytes": outside.stat().st_size,
                        "lines": 1,
                    },
                },
            )
            self.assertEqual(
                2,
                main([
                    "--ledger", str(ledger),
                    "--repo", str(root),
                    "view",
                    "--id", "EV-ESCAPE",
                    "--stream", "stdout",
                    "--tail", "1",
                ]),
            )

    def test_custom_captured_artifact_inside_repo_counts_as_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git_repo(root)
            ledger = root / ".verification" / "evidence.jsonl"
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    0,
                    main([
                        "--ledger", str(ledger),
                        "--repo", str(root),
                        "--artifact-dir", str(root / "captured-output"),
                        "run",
                        "--id", "EV-ART",
                        "--label", "Captured in repo",
                        "--capture-output",
                        "--",
                        sys.executable,
                        "-c",
                        "print('ok')",
                    ]),
                )
            state = current_states(load_events(ledger), repository_snapshot(root))[0]
            self.assertEqual("mutated", state.status)


if __name__ == "__main__":
    unittest.main()
