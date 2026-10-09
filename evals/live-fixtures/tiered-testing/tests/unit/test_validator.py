import unittest
from validator import valid_slug


class ValidatorUnitTests(unittest.TestCase):
    def test_simple_slug(self):
        self.assertTrue(valid_slug("alpha1"))

    def test_hyphenated_slug(self):
        self.assertTrue(valid_slug("alpha-beta"))

    def test_rejects_spaces(self):
        self.assertFalse(valid_slug("alpha beta"))


if __name__ == "__main__":
    unittest.main()
