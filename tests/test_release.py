from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.generate_manifest import build_manifest
from scripts.package_release import write_release


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_manifest_excludes_itself_and_contains_hashes(self):
        manifest = build_manifest(ROOT)
        self.assertIn("# FILE_MANIFEST v1", manifest)
        self.assertNotIn("\tFILE_MANIFEST.txt\n", manifest)
        self.assertIn("\tREADME.md\n", manifest)

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


if __name__ == "__main__":
    unittest.main()
