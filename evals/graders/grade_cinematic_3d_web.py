#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
html_path = root / "index.html"
js_path = root / "scene.js"
plan_path = root / "PRODUCTION_PLAN.md"

if not html_path.is_file() or not js_path.is_file():
    print("index.html and scene.js must remain present")
    raise SystemExit(1)

html = html_path.read_text(encoding="utf-8")
js = js_path.read_text(encoding="utf-8")
plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""

checks = []

checks.append((
    plan_path.is_file(),
    "PRODUCTION_PLAN.md is required so shot/layer decisions exist before polish",
))

plan_lower = plan.lower()
for term in ("visual contract", "shot", "layer", "mobile", "reduced motion", "performance"):
    checks.append((
        term in plan_lower,
        f"PRODUCTION_PLAN.md should discuss {term}",
    ))

checks.append((
    bool(re.search(r"Math\.min\s*\([^)]*(?:devicePixelRatio|pixelRatio)[^)]*,\s*(?:1(?:\.\d+)?|2(?:\.\d+)?)", js, re.I | re.S))
    or bool(re.search(r"(?:DPR_CAP|MAX_DPR|dprCap)\s*=\s*(?:1(?:\.\d+)?|2(?:\.\d+)?)", js, re.I)),
    "scene.js needs a bounded DPR/render-scale policy",
))

checks.append((
    "prefers-reduced-motion" in js,
    "scene.js needs a reduced-motion path",
))

checks.append((
    bool(re.search(r"(?:shots|SHOT_STATES|cameraStates)\s*=", js))
    and len(re.findall(r"(?:position|pos)\s*:", js)) >= 3,
    "scene.js should author at least three camera shot states as data",
))

checks.append((
    ("scrollY" in js or "scrollTop" in js)
    and ("requestAnimationFrame" in js or "raf" in js.lower()),
    "scroll choreography should be driven through a requestAnimationFrame-coalesced conductor",
))

checks.append((
    "visibilitychange" in js or "document.hidden" in js,
    "render work should react to hidden-page visibility",
))

checks.append((
    bool(re.search(r"(?:poster|fallback|webgl-fallback|no-webgl)", js, re.I)),
    "scene.js needs a visible WebGL failure/static fallback",
))

checks.append((
    "<h1" in html.lower()
    and "<main" in html.lower()
    and bool(re.search(r"<a[^>]+href=[\"']#core[\"']", html, re.I)),
    "semantic DOM story content and the real anchor CTA must remain outside the canvas",
))

checks.append((
    not bool(re.search(r"https?://", html + "\n" + js, re.I)),
    "the fixture should not gain remote runtime dependencies",
))

failed = [msg for ok, msg in checks if not ok]
if failed:
    for msg in failed:
        print(msg)
    raise SystemExit(1)

print("cinematic-3d-web=pass")
