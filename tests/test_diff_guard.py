from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.diff_guard import collect_changes, parse_numstat, summarize


class DiffGuardTests(unittest.TestCase):
    def test_parse_numstat_handles_binary(self):
        changes = parse_numstat("10\t2\tsrc/a.ts\n-\t-\tassets/a.png\n")
        self.assertEqual(2, len(changes))
        self.assertEqual(12, changes[0].churn)
        self.assertIsNone(changes[1].added)

    def test_broad_scope_signals(self):
        text = "\n".join(f"50\t30\tarea{i}/file{i}.ts" for i in range(10))
        summary = summarize(parse_numstat(text))
        self.assertGreaterEqual(summary["files_changed"], 10)
        self.assertGreaterEqual(len(summary["top_level_areas"]), 6)
        self.assertGreaterEqual(summary["churn"], 700)
        self.assertGreaterEqual(len(summary["signals"]), 3)

    def test_collect_changes_includes_untracked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "tests@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tests"], check=True)
            (repo / "README.md").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "base"], check=True)

            for index in range(25):
                folder = repo / f"area{index}"
                folder.mkdir()
                (folder / "new.ts").write_text("export const x = 1;\n", encoding="utf-8")

            changes = collect_changes(repo, "HEAD")
            summary = summarize(changes)
            self.assertEqual(25, summary["untracked_files"])
            self.assertEqual(25, summary["files_changed"])
            self.assertIn("20+ files changed", summary["signals"])
            self.assertIn("6+ top-level areas touched", summary["signals"])

    def test_commit_to_commit_diff_does_not_mix_worktree_untracked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "tests@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tests"], check=True)
            (repo / "a.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "one"], check=True)
            first = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            (repo / "a.txt").write_text("two\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "commit", "-qam", "two"], check=True)
            second = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            (repo / "untracked.txt").write_text("not part of commit range\n", encoding="utf-8")

            changes = collect_changes(repo, first, second)
            self.assertEqual(["a.txt"], [change.path for change in changes])


if __name__ == "__main__":
    unittest.main()
