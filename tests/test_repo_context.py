from pathlib import Path
import json, tempfile, unittest
from scripts.repo_context import build_context, render_text

class RepoContextTests(unittest.TestCase):
    def test_maps_instructions_versions_commands_and_nearby_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'AGENTS.md').write_text('# rules\n',encoding='utf-8')
            (root/'package.json').write_text(json.dumps({'engines':{'node':'>=22'},'dependencies':{'next':'16.1.0'},'scripts':{'test':'x','build':'y'}}),encoding='utf-8')
            feature=root/'src'/'accounts'; feature.mkdir(parents=True)
            (feature/'service.ts').write_text('export const x=1;\n',encoding='utf-8')
            tests=feature/'tests'; tests.mkdir(); (tests/'service.test.ts').write_text('test(1)\n',encoding='utf-8')
            docs=root/'docs'; docs.mkdir(); (docs/'GLOSSARY.md').write_text('materialization cascade: secret expansion text\n',encoding='utf-8')
            data=build_context(root, feature)
            self.assertIn('AGENTS.md',data['instructions'])
            self.assertEqual('16.1.0',data['versions']['next'])
            self.assertIn('npm run test',data['likely_commands'])
            self.assertIn('src/accounts/service.ts',data['nearby_source'])
            self.assertIn('src/accounts/tests/service.test.ts',data['nearby_tests'])
            self.assertIn('docs/GLOSSARY.md',data['vocabulary_sources'])
            rendered=render_text(data)
            self.assertIn('docs/GLOSSARY.md',rendered)
            self.assertNotIn('materialization cascade',rendered)
            self.assertNotIn('secret expansion text',rendered)
            self.assertNotIn('test(1)',rendered)

    def test_rejects_missing_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): build_context(Path(tmp)/'missing')

if __name__=='__main__': unittest.main()
