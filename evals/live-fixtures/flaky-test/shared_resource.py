from pathlib import Path

STATE = Path(".shared-port-owner")


def acquire_port() -> bool:
    # BUG: a process-global fixed resource leaks across repeated test runs.
    if STATE.exists():
        STATE.unlink()
        return False
    STATE.write_text("owned", encoding="utf-8")
    return True
