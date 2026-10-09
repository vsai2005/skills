from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import os
import sys
import time
import tempfile
import unittest

from scripts.flake_check import main, recommended_runs_for_detection, run_repeated, summarize, wilson_interval


class FlakeCheckTests(unittest.TestCase):
    def test_all_passes_have_zero_failure_rate(self):
        results = run_repeated([sys.executable, "-c", "raise SystemExit(0)"], 3)
        stats = summarize(results)
        self.assertEqual(3, stats["runs"])
        self.assertEqual(0, stats["failures"])
        self.assertEqual(0.0, stats["failure_rate"])

    def test_reports_observed_failure_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            counter = Path(tmp) / "counter.txt"
            code = (
                "from pathlib import Path; import sys; "
                f"p=Path({str(counter)!r}); n=int(p.read_text()) if p.exists() else 0; "
                "p.write_text(str(n+1)); print('same failure' if n % 2 == 0 else 'pass'); raise SystemExit(1 if n % 2 == 0 else 0)"
            )
            results = run_repeated([sys.executable, "-c", code], 4)
            stats = summarize(results)
            self.assertEqual(2, stats["failures"])
            self.assertEqual(0.5, stats["failure_rate"])
            self.assertEqual([1, 0, 1, 0], [result.exit_code for result in results])
            self.assertEqual(1, len(stats["failure_signatures"]))

    def test_json_mode_stays_valid_when_child_prints(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--runs", "1", "--json", "--", sys.executable, "-c", "print('child output')"])
        self.assertEqual(0, code)
        parsed = json.loads(output.getvalue())
        self.assertEqual("child output\n", parsed["results"][0]["stdout"])

    def test_timeout_is_inconclusive(self):
        results = run_repeated([sys.executable, "-c", "import time; time.sleep(1)"], 1, timeout=0.05)
        self.assertEqual("timeout", results[0].outcome)
        self.assertEqual(1, summarize(results)["inconclusive_runs"])

    def test_required_output_detects_zero_test_success(self):
        results = run_repeated([sys.executable, "-c", "print('0 tests collected')"], 1, require_output_regex=r"1 passed")
        self.assertEqual("zero-tests", results[0].outcome)

    def test_infrastructure_exit_code_is_not_counted_as_test_failure(self):
        results = run_repeated([sys.executable, "-c", "raise SystemExit(75)"], 1, infrastructure_exit_codes={75})
        stats = summarize(results)
        self.assertEqual("infrastructure-error", results[0].outcome)
        self.assertEqual(0, stats["failures"])
        self.assertEqual(1, stats["infrastructure_errors"])

    def test_wilson_interval_for_zero_failures_is_not_zero_width(self):
        interval = wilson_interval(0, 20)
        self.assertIsNotNone(interval)
        assert interval is not None
        self.assertEqual(0.0, interval[0])
        self.assertGreater(interval[1], 0.0)


    def test_rate_based_run_recommendation(self):
        self.assertEqual(59, recommended_runs_for_detection(0.05, 0.95))
        self.assertEqual(14, recommended_runs_for_detection(0.20, 0.95))

    def test_rate_based_recommendation_rejects_invalid_values(self):
        for rate in (0.0, 1.0, -0.1, 1.1):
            with self.assertRaises(ValueError):
                recommended_runs_for_detection(rate, 0.95)
        with self.assertRaises(ValueError):
            recommended_runs_for_detection(0.05, 1.0)

    def test_cli_uses_rate_based_n_when_runs_omitted(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([
                "--expected-rate", "0.5",
                "--detection-confidence", "0.75",
                "--json",
                "--", sys.executable, "-c", "raise SystemExit(0)",
            ])
        self.assertEqual(0, code)
        parsed = json.loads(output.getvalue())
        self.assertEqual(2, parsed["planning"]["recommended_runs"])
        self.assertEqual(2, parsed["planning"]["planned_runs"])
        self.assertEqual(2, parsed["summary"]["runs"])

    def test_rejects_zero_runs(self):
        with self.assertRaises(ValueError):
            run_repeated([sys.executable, "-c", "pass"], 0)

    def test_signature_uses_stdout_and_stderr_together(self):
        a = run_repeated([sys.executable, "-c", "import sys; print('FAIL A'); print('warning', file=sys.stderr); raise SystemExit(1)"], 1)[0]
        b = run_repeated([sys.executable, "-c", "import sys; print('FAIL B'); print('warning', file=sys.stderr); raise SystemExit(1)"], 1)[0]
        self.assertNotEqual(a.signature, b.signature)
        self.assertIn("FAIL A", a.signature_excerpt or "")

    def test_nonzero_zero_test_exit_code_is_inconclusive(self):
        results = run_repeated([sys.executable, "-c", "print('no tests'); raise SystemExit(5)"], 1, zero_test_exit_codes={5})
        self.assertEqual("zero-tests", results[0].outcome)
        self.assertEqual(0, summarize(results)["failures"])

    def test_timeout_terminates_spawned_child_process(self):
        if os.name != "posix":
            result = run_repeated([sys.executable, "-c", "import time; time.sleep(5)"], 1, timeout=0.05)[0]
            self.assertEqual("timeout", result.outcome)
            return
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / "child-lived.txt"
            child = f"import time; from pathlib import Path; time.sleep(0.4); Path({str(sentinel)!r}).write_text('alive')"
            parent = f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(5)"
            result = run_repeated([sys.executable, "-c", parent], 1, timeout=0.05)[0]
            self.assertEqual("timeout", result.outcome)
            time.sleep(0.6)
            self.assertFalse(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
