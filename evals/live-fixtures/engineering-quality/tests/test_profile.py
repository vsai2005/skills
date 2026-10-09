import unittest
from api import profile


class ProfileTests(unittest.TestCase):
    def test_old_record(self):
        self.assertEqual({"display_name": "Ada"}, profile({"name": "Ada"}))


if __name__ == "__main__":
    unittest.main()
