import subprocess
from pathlib import Path

root = Path.cwd()
def run(*args):
    subprocess.run(args, cwd=root, check=True, stdout=subprocess.DEVNULL)

run("git", "init", "-q")
run("git", "config", "user.email", "fixture@example.invalid")
run("git", "config", "user.name", "Fixture")
(root / "run_tests.py").write_text(
    'print("FAIL test.preexisting: provider unavailable")\nraise SystemExit(1)\n',
    encoding="utf-8",
)
run("git", "add", "run_tests.py")
run("git", "commit", "-q", "-m", "baseline")
(root / "run_tests.py").write_text(
    'print("FAIL test.preexisting: provider unavailable")\nprint("FAIL test.regression: expected 403 got 200")\nraise SystemExit(1)\n',
    encoding="utf-8",
)
run("git", "add", "run_tests.py")
run("git", "commit", "-q", "-m", "candidate regression")

Path(__file__).unlink()
