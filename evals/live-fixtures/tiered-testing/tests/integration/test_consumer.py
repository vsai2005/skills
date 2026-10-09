import unittest
from validator import valid_slug


class ConsumerIntegrationTests(unittest.TestCase):
    def test_service_accepts_shared_hyphen_rule(self):
        self.assertTrue(valid_slug("billing-api"))


if __name__ == "__main__":
    unittest.main()
