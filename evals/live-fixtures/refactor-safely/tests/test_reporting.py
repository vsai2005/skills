import unittest
from reporting import generate_report


class ReportingTests(unittest.TestCase):
    def test_public_behavior(self):
        self.assertEqual(
            "NAME | SCORE\n------------\nAda | 9\nBob | 5\n------------\nTOTAL | 14",
            generate_report([{"name": "Bob", "score": 5}, {"name": " Ada ", "score": 9}]),
        )

    def test_invalid_name(self):
        with self.assertRaisesRegex(ValueError, "name required"):
            generate_report([{"name": " ", "score": 1}])


if __name__ == "__main__":
    unittest.main()
