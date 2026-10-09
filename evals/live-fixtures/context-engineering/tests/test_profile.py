import unittest
from profile import format_profile

class ProfileTests(unittest.TestCase):
    def test_formats_profile(self):
        self.assertEqual("User: Ada Lovelace", format_profile("ada", "lovelace"))

if __name__ == "__main__": unittest.main()
