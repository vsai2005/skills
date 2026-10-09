import unittest
from access import update_project_owner

class AccessTests(unittest.TestCase):
    def test_current_owner_can_transfer(self):
        self.assertEqual("bob", update_project_owner("alice", "member", "alice", "bob"))

    def test_admin_can_transfer(self):
        self.assertEqual("bob", update_project_owner("root", "admin", "alice", "bob"))

if __name__ == "__main__": unittest.main()
