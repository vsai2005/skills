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

focus_match = re.search(r":focus(?:-visible)?[^{}]*\{([^}]*)\}", css, re.I | re.S)
focus_body = focus_match.group(1).lower() if focus_match else ""
custom_focus = (
    bool(re.search(r"outline\s*:\s*(?!none|0)[^;]+", focus_body))
    or "box-shadow" in focus_body
    or bool(re.search(r"border(?:-color)?\s*:", focus_body))
)
outline_removed = bool(re.search(r"outline\s*:\s*(?:none|0)(?:\s*;|\s*$)", css, re.I | re.M))
checks.append((
    bool(focus_match) and (not outline_removed or custom_focus),
    "visible focus styling is missing or focus is removed without a replacement",
))

checks.append((
    bool(re.search(r"(?:min-height|height)\s*:\s*(?:4[4-9]|[5-9]\d|\d{3,})px\b", css, re.I)),
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
    'role="alert"' in html.lower()
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
