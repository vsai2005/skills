from pathlib import Path
import unittest
from scripts.portability_check import check
ROOT=Path(__file__).resolve().parents[1]
class PortabilityTests(unittest.TestCase):
    def test_repository_is_portable(self):
        result=check(ROOT)
        self.assertEqual([],result['errors'])
        self.assertEqual([],result['warnings'])
        self.assertGreaterEqual(len(result['skills']),15)
