from pathlib import Path
import json
import tempfile
import unittest

from scripts.live_eval import _arm_order, _run_arm, build_parser, main as live_eval_main
from scripts.live_eval_graders import grade_case
from scripts.live_eval_support import (
    build_claude_command,
    build_codex_command,
    load_live_cases,
    normalize_trace,
    prepare_prompt_skill,
    git_diff_metrics,
    trace_workflow_metrics,
)


ROOT = Path(__file__).resolve().parents[1]


class LiveEvalTests(unittest.TestCase):
    def test_real_live_cases_cover_all_skills(self):
        cases = load_live_cases(ROOT / "evals" / "live-cases.json", ROOT)
        covered = {case["skill"] for case in cases}
        expected = {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}
        self.assertEqual(expected, covered)
        self.assertGreaterEqual(len(cases), 14)


    def test_arm_order_alternates_to_reduce_time_order_bias(self):
        self.assertEqual(("control", "treatment"), _arm_order(1, "alternate"))
        self.assertEqual(("treatment", "control"), _arm_order(2, "alternate"))

    def test_dry_run_records_version_bound_provenance(self):
        cases = load_live_cases(ROOT / "evals" / "live-cases.json", ROOT)
        case = cases[0]
        with tempfile.TemporaryDirectory() as tmp:
            record = _run_arm(
                repo=ROOT, case=case, provider="codex", binary="codex", model="model-x",
                mode="treatment", repetition=1, out_root=Path(tmp), campaign_id="campaign-x",
                suite_sha256="suite-x", timeout_seconds=30, max_budget_usd=None, command_json=None, dry_run=True,
            )
            self.assertEqual(2, record["schema_version"])
            self.assertEqual("campaign-x", record["campaign_id"])
            self.assertEqual("suite-x", record["suite_sha256"])
            self.assertRegex(record["case_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(record["skill_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual([case["skill"]], record["enabled_skills"])

    def test_parser_accepts_repeated_models_for_matrix(self):
        args = build_parser().parse_args(["run", "--provider", "codex", "--model", "m1", "--model", "m2", "--dry-run"])
        self.assertEqual(["m1", "m2"], args.model)

    def test_codex_command_uses_structured_automation_mode(self):
        command = build_codex_command("codex", "fix it", model="gpt-test")
        self.assertEqual("codex", command[0])
        self.assertIn("exec", command)
        self.assertIn("--json", command)
        self.assertIn("--full-auto", command)
        self.assertIn("--model", command)
        self.assertEqual("fix it", command[-1])

    def test_claude_treatment_loads_only_eval_plugin(self):
        command = build_claude_command(
            "claude",
            "fix it",
            plugin_dir=Path("/tmp/plugin"),
            control=False,
            model="sonnet",
            max_budget_usd=1.25,
        )
        self.assertIn("-p", command)
        self.assertIn("stream-json", command)
        self.assertIn("--plugin-dir", command)
        self.assertNotIn("--disable-slash-commands", command)
        self.assertIn("--max-budget-usd", command)

    def test_claude_control_disables_skills(self):
        command = build_claude_command(
            "claude",
            "fix it",
            plugin_dir=None,
            control=True,
        )
        self.assertIn("--disable-slash-commands", command)
        self.assertNotIn("--plugin-dir", command)

    def test_prompt_skill_mount_is_readable_and_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            target, instruction = prepare_prompt_skill(
                workspace,
                ROOT / "skills" / "debug-root-cause",
                "debug-root-cause",
            )
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertIn(".eval-skill/debug-root-cause/SKILL.md", instruction)

    def test_graders_score_files_trace_and_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            (workspace / "out.txt").write_text("hello world\n", encoding="utf-8")
            graders = [
                {"id": "exists", "type": "file_exists", "path": "out.txt", "weight": 1},
                {"id": "content", "type": "file_contains", "path": "out.txt", "text": "hello", "weight": 2},
                {"id": "trace", "type": "trace_regex", "pattern": "pytest", "weight": 1},
                {"id": "command", "type": "command", "argv": ["python3", "-c", "raise SystemExit(0)"], "weight": 2},
            ]
            results, score, max_score, fraction = grade_case(
                graders,
                workspace=workspace,
                repo=ROOT,
                run_dir=Path(tmp),
                trace="ran pytest -q",
                changed_files=["out.txt"],
            )
            self.assertTrue(all(item["passed"] for item in results))
            self.assertEqual(max_score, score)
            self.assertEqual(1.0, fraction)

    def test_normalize_trace_extracts_json_text(self):
        stdout = '{"type":"result","result":"done"}\n'
        trace, final = normalize_trace(stdout, "warning")
        self.assertIn("done", trace)
        self.assertIn("warning", trace)
        self.assertEqual("done", final)

    def test_full_arm_retains_artifacts_with_custom_provider(self):
        cases = load_live_cases(ROOT / "evals" / "live-cases.json", ROOT)
        case = next(item for item in cases if item["id"] == "debug-root-cause-classifier-live")
        with tempfile.TemporaryDirectory() as tmp:
            record = _run_arm(
                repo=ROOT,
                case=case,
                provider="command",
                binary="",
                model=None,
                mode="control",
                repetition=1,
                out_root=Path(tmp),
                timeout_seconds=30,
                max_budget_usd=None,
                command_json=json.dumps(["python3", "-c", "import json; print(json.dumps({\"type\":\"result\",\"result\":\"done\"}))"]),
                dry_run=False,
            )
            self.assertEqual("completed", record["status"])
            self.assertLess(record["score_fraction"], 1.0)
            artifact = Path(record["artifact_dir"])
            self.assertTrue((artifact / "stdout.log").is_file())
            self.assertTrue((artifact / "result.json").is_file())
            self.assertTrue((artifact / "changed-files.json").is_file())
            self.assertTrue((artifact / "workflow-metrics.json").is_file())
            self.assertIn("workflow_metrics", record)

    def test_workflow_metrics_measure_scope_and_trace_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            import subprocess
            subprocess.run(["git", "init", "-q", str(workspace)], check=True)
            subprocess.run(["git", "-C", str(workspace), "config", "user.email", "t@example.com"], check=True)
            subprocess.run(["git", "-C", str(workspace), "config", "user.name", "T"], check=True)
            (workspace / "a.py").write_text("x=1\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(workspace), "add", "a.py"], check=True)
            subprocess.run(["git", "-C", str(workspace), "commit", "-qm", "base"], check=True)
            (workspace / "a.py").write_text("x=2\n", encoding="utf-8")
            (workspace / "extra.txt").write_text("extra\n", encoding="utf-8")
            metrics = git_diff_metrics(workspace, ["a.py", "extra.txt"], ["a.py"])
            self.assertEqual(2, metrics["changed_file_count"])
            self.assertGreaterEqual(metrics["diff_churn"], 2)
            self.assertEqual(1, metrics["unrelated_file_count"])
            trace = trace_workflow_metrics('{"type":"tool_call","name":"read_file","path":"a.py"}\n{"type":"tool_call","name":"read_file","path":"a.py"}', "")
            self.assertGreaterEqual(trace["tool_event_count"], 2)


    def test_external_git_fixture_validates_and_dry_run_does_not_clone(self):
        cases = load_live_cases(ROOT / "evals" / "historical-debug-cases.json", ROOT)
        self.assertEqual(2, len(cases))
        self.assertIn("git_fixture", cases[0])
        with tempfile.TemporaryDirectory() as tmp:
            code = live_eval_main([
                "run",
                "--cases", str(ROOT / "evals" / "historical-debug-cases.json"),
                "--provider", "codex",
                "--runs", "1",
                "--case", "historical-pytest-11143-numeric-docstring",
                "--output-dir", tmp,
                "--dry-run",
            ])
            self.assertEqual(0, code)
            records = [json.loads(line) for line in (Path(tmp) / "codex-runs.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(records))
            self.assertTrue(all(item["status"] == "planned" for item in records))

    def test_invalid_live_case_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live.json"
            path.write_text('[{"id":"x","skill":"missing","fixture":"nope","request":"r","graders":[]}]', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_live_cases(path, ROOT)


if __name__ == "__main__":
    unittest.main()
