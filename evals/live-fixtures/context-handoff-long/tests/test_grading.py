import unittest
from grading import passes

class GradingTests(unittest.TestCase):
    def test_clear_pass(self): self.assertTrue(passes(90))
    def test_clear_fail(self): self.assertFalse(passes(40))

if __name__ == '__main__': unittest.main()
