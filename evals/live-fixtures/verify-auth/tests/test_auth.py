import unittest
from auth import status_for_role


class AuthTests(unittest.TestCase):
    def test_admin_allowed(self):
        self.assertEqual(200, status_for_role("admin"))

    def test_viewer_forbidden(self):
        self.assertEqual(403, status_for_role("viewer"))

    def test_unknown_unauthorized(self):
        self.assertEqual(401, status_for_role("anonymous"))


if __name__ == "__main__":
    unittest.main()
