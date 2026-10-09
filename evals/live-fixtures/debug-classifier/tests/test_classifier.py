import unittest
from classifier import has_foreign_topic


class ClassifierTests(unittest.TestCase):
    def test_javascript_is_allowed(self):
        self.assertFalse(has_foreign_topic("Explain JavaScript arrays"))

    def test_java_is_foreign(self):
        self.assertTrue(has_foreign_topic("Explain Java generics"))

    def test_go_is_foreign(self):
        self.assertTrue(has_foreign_topic("Explain Go channels"))


if __name__ == "__main__":
    unittest.main()
