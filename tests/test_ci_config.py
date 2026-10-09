from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class CiConfigTests(unittest.TestCase):
    def test_ci_has_windows_lane_and_pinned_actions(self):
        text=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('windows-latest',text)
        self.assertIn('actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1',text)
        self.assertIn('actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97',text)
        self.assertNotIn('actions/checkout@v',text)
        self.assertNotIn('actions/setup-python@v',text)
    def test_dependabot_is_actions_only(self):
        text=(ROOT/'.github/dependabot.yml').read_text(encoding='utf-8')
        self.assertIn('package-ecosystem: "github-actions"',text)
        self.assertNotIn('pip',text)
