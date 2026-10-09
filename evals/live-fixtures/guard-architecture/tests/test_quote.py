import unittest
from web import quote_response


class QuoteTests(unittest.TestCase):
    def test_quote(self):
        self.assertEqual({"final_cents": 900}, quote_response(1000, 10))


if __name__ == "__main__":
    unittest.main()
