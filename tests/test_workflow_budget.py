import unittest
from scripts.workflow_budget import assess
class WorkflowBudgetTests(unittest.TestCase):
    def test_repeated_same_failure_forces_reset(self): self.assertTrue(any('rebuild the hypothesis' in x for x in assess('L1',2,2,0,10,1)))
    def test_normal_small_change_has_no_signal(self): self.assertEqual([],assess('L1',1,0,0,20,1))
