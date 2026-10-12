import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "evals" / "graders" / "grade_ui_ux_quality.py"
FIXTURE = ROOT / "evals" / "live-fixtures" / "ui-ux-quality"


class UiUxQualityGraderTests(unittest.TestCase):
    def run_grader(self, workspace: Path):
        return subprocess.run(
            [sys.executable, str(GRADER), str(workspace)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_broken_fixture_is_rejected(self):
        result = self.run_grader(FIXTURE)
        self.assertNotEqual(0, result.returncode)

    def test_representative_accessible_responsive_repair_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "index.html").write_text(
                """<!doctype html>
<html lang="en">
<body>
  <main class="checkout-card">
    <form>
      <label for="email">Email address</label>
      <input id="email" name="email" type="email">
      <button type="submit">Pay now</button>
      <p role="alert" hidden>Payment failed. Try again.</p>
    </form>
  </main>
</body>
</html>
""",
                encoding="utf-8",
            )
            (workspace / "styles.css").write_text(
                """.checkout-card { width: 100%; max-width: 720px; }
button { height: 44px; }
button:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
""",
                encoding="utf-8",
            )
            (workspace / "UX_REVIEW.md").write_text(
                "# UX Review\nChecked mobile layout, focus visibility, persistent label behavior, and error/loading state feedback.\n",
                encoding="utf-8",
            )
            result = self.run_grader(workspace)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
