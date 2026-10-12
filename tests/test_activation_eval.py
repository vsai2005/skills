from pathlib import Path
import tempfile
import unittest

from scripts.activation_eval import (
    _all_skills,
    build_parser,
    detect_loaded_skills,
    load_cases,
    prepare_invocation,
)


ROOT = Path(__file__).resolve().parents[1]


class ActivationEvalTests(unittest.TestCase):
    def test_cases_load_against_current_skill_set(self):
        skills = {name for name, _ in _all_skills(ROOT)}
        cases = load_cases(ROOT / "evals" / "activation-cases.json", skills)
        self.assertGreaterEqual(len(cases), 50)
        self.assertTrue(any(case["expected_primary_skill"] == "none" for case in cases))

    def test_trace_detection_preserves_first_observed_skill(self):
        trace = (
            'read_file path=.agents/skills/debug-root-cause/SKILL.md\n'
            'read_file path=.agents/skills/verify-change/SKILL.md\n'
        )
        observed = detect_loaded_skills(trace, ["verify-change", "debug-root-cause"])
        self.assertEqual(["debug-root-cause", "verify-change"], observed)

    def test_antigravity_activation_mounts_all_skills_in_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            workspace = base / "workspace"
            run_dir = base / "run"
            workspace.mkdir()
            run_dir.mkdir()
            argv, env, strategy = prepare_invocation(
                provider="antigravity",
                binary="agy",
                model="model-x",
                prompt="Fix this parser bug.",
                repo=ROOT,
                workspace=workspace,
                run_dir=run_dir,
                command_json=None,
            )
            self.assertIsNone(env)
            self.assertEqual("native-workspace-skills", strategy)
            self.assertIn("stream-json", argv)
            mounted = {
                path.parent.name
                for path in (workspace / ".agents" / "skills").glob("*/SKILL.md")
            }
            self.assertEqual({name for name, _ in _all_skills(ROOT)}, mounted)

    def test_parser_accepts_dry_run_provider_matrix(self):
        parser = build_parser()
        for provider in ("codex", "claude", "antigravity", "command"):
            args = ["run", "--provider", provider, "--dry-run"]
            if provider == "command":
                args += ["--command-json", '["echo","{prompt}"]']
            parsed = parser.parse_args(args)
            self.assertEqual(provider, parsed.provider)


if __name__ == "__main__":
    unittest.main()
