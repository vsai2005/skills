import unittest
from scripts.instruction_ablation import remove_section
class AblationTests(unittest.TestCase):
    def test_remove_named_section_only(self):
        text='# X\n\n## A\none\n\n### A1\ntwo\n\n## B\nthree\n'
        out=remove_section(text,'A')
        self.assertNotIn('one',out); self.assertNotIn('A1',out); self.assertIn('## B',out)

    def test_numbered_heading_can_be_named_without_number(self):
        text='# X\n\n## 2. Investigate cause\nbody\n\n## 3. Verify\nkeep\n'
        out=remove_section(text,'Investigate cause')
        self.assertNotIn('body',out); self.assertIn('## 3. Verify',out)
