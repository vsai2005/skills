#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
html = (root / "index.html").read_text(encoding="utf-8")
css = (root / "styles.css").read_text(encoding="utf-8")
report_path = root / "UX_REVIEW.md"

checks = []

checks.append((
    bool(re.search(r'<label[^>]+for=["\']email["\']', html, re.I))
    and bool(re.search(r'<input[^>]+id=["\']email["\']', html, re.I)),
    "email input needs a persistent associated label",
))
checks.append((
    "outline: none" not in css.lower() and "outline:none" not in css.lower(),
    "focus must not be globally removed",
))
checks.append((
    ":focus-visible" in css or ":focus" in css,
    "explicit visible focus styling is missing",
))
checks.append((
    bool(re.search(r"min-height\s*:\s*(?:4[4-9]|[5-9]\d|\d{3,})px", css, re.I)),
    "interactive targets need a usable minimum height",
))
checks.append((
    "width: 720px" not in css.lower()
    and (
        "max-width" in css.lower()
        or "width: min(" in css.lower()
        or "@media" in css.lower()
    ),
    "fixed checkout width still risks narrow-screen overflow",
))
checks.append((
    "role=\"alert\"" in html.lower()
    or "role='alert'" in html.lower()
    or "aria-live=" in html.lower(),
    "error/status state is not exposed accessibly",
))
checks.append((
    report_path.is_file(),
    "UX_REVIEW.md is missing",
))

failed = [message for ok, message in checks if not ok]
if failed:
    for message in failed:
        print(message)
    raise SystemExit(1)

report = report_path.read_text(encoding="utf-8").lower()
for term in ("mobile", "focus", "label", "state"):
    if term not in report:
        print(f"UX_REVIEW.md should discuss {term}")
        raise SystemExit(1)

print("ui-ux-quality=pass")
