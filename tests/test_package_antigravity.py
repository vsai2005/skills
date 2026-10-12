from pathlib import Path
import json
import tempfile
import unittest
import zipfile

from scripts.package_antigravity import (
    ANTIGRAVITY_SCHEMA,
    PLUGIN_NAME,
    write_antigravity_plugin,
)
from scripts.release_common import sha256_file


ROOT = Path(__file__).resolve().parents[1]


class AntigravityPackageTests(unittest.TestCase):
    def test_builds_strict_manifest_and_all_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage, zip_path, checksum_path = write_antigravity_plugin(ROOT, Path(tmp))

            manifest = json.loads((stage / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(
                {"$schema", "name", "description"},
                set(manifest),
            )
            self.assertEqual(ANTIGRAVITY_SCHEMA, manifest["$schema"])
            self.assertEqual(PLUGIN_NAME, manifest["name"])

            source_skills = {
                p.name for p in (ROOT / "skills").iterdir()
                if p.is_dir() and (p / "SKILL.md").is_file()
            }
            bundled_skills = {
                p.name for p in (stage / "skills").iterdir()
                if p.is_dir() and (p / "SKILL.md").is_file()
            }
            self.assertEqual(source_skills, bundled_skills)
            self.assertEqual(16, len(bundled_skills))
            self.assertTrue(zip_path.is_file())
            self.assertTrue(checksum_path.is_file())

    def test_zip_is_valid_and_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            _, zip_a, _ = write_antigravity_plugin(ROOT, Path(a))
            _, zip_b, _ = write_antigravity_plugin(ROOT, Path(b))
            self.assertEqual(sha256_file(zip_a), sha256_file(zip_b))
            with zipfile.ZipFile(zip_a) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertTrue(any(name.endswith("/plugin.json") for name in names))
                self.assertTrue(any(name.endswith("/skills/project-quality-orchestrator/SKILL.md") for name in names))


if __name__ == "__main__":
    unittest.main()
