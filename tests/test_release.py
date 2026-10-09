from pathlib import Path
import os
import subprocess
import tempfile
import unittest
import zipfile

from scripts.generate_manifest import build_manifest
from scripts.package_release import require_no_pending_tests, write_release
from scripts.pending_tests import add_item
from scripts.release_common import iter_release_files


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_manifest_excludes_itself_and_contains_hashes(self):
        manifest = build_manifest(ROOT)
        self.assertIn("# FILE_MANIFEST v1", manifest)
        self.assertNotIn("\tFILE_MANIFEST.txt\n", manifest)
        self.assertIn("\tREADME.md\n", manifest)

    def test_verification_ledger_is_not_a_release_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".verification").mkdir()
            (root / ".verification" / "evidence.jsonl").write_text('{"secret":"local evidence"}\n', encoding="utf-8")
            (root / "dist").mkdir()
            (root / "dist" / "old-release.zip").write_bytes(b"old")
            (root / "README.md").write_text("ok\n", encoding="utf-8")
            names = {path.relative_to(root).as_posix() for path in iter_release_files(root)}
            self.assertIn("README.md", names)
            self.assertNotIn(".verification/evidence.jsonl", names)
            self.assertNotIn("dist/old-release.zip", names)

    def test_package_checksum_is_portable_and_zip_has_single_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path, checksum_path = write_release(ROOT, Path(tmp))
            checksum_text = checksum_path.read_text(encoding="utf-8").strip()
            self.assertTrue(checksum_text.endswith(f"  {zip_path.name}"))
            self.assertNotIn(str(zip_path.parent), checksum_text)
            with zipfile.ZipFile(zip_path) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertTrue(names)
                self.assertTrue(all(name.startswith("engineering-quality-agent-skills/") for name in names))
                self.assertIn("engineering-quality-agent-skills/FILE_MANIFEST.txt", names)
                self.assertFalse(any("/.verification/" in name for name in names))

    def test_git_release_uses_tracked_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "README.md").write_text("ok\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            (root / "untracked.txt").write_text("must not ship\n", encoding="utf-8")
            (root / ".env").write_text("API_KEY=secret\n", encoding="utf-8")
            names = {path.relative_to(root).as_posix() for path in iter_release_files(root)}
            self.assertEqual({"README.md"}, names)

    def test_tracked_sensitive_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".env").write_text("API_KEY=secret\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", ".env"], check=True)
            with self.assertRaisesRegex(ValueError, "sensitive filename"):
                list(iter_release_files(root))

    def test_source_archive_sensitive_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text("API_KEY=secret\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sensitive filename"):
                list(iter_release_files(root))

    def test_external_symlink_is_rejected_in_source_archive(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            secret = Path(outside) / "secret.txt"
            secret.write_text("TOPSECRET\n", encoding="utf-8")
            os.symlink(secret, root / "leak.txt")
            with self.assertRaisesRegex(ValueError, "symlink"):
                list(iter_release_files(root))

    def test_release_is_blocked_by_pending_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / "PENDING_TESTS.md"
            add_item(pending, "python -m unittest", "heavy suite", "before release")
            with self.assertRaisesRegex(ValueError, "release blocked"):
                require_no_pending_tests(root)

    def test_missing_tracked_file_blocks_release_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            target = root / "tracked.txt"
            target.write_text("present\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
            target.unlink()
            with self.assertRaisesRegex(ValueError, "missing from worktree"):
                list(iter_release_files(root))


if __name__ == "__main__":
    unittest.main()
