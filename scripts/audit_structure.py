#!/usr/bin/env python3
"""Conservative, heuristic source-structure audit.

This does not replace language-aware linters or static analysis. It surfaces
review prompts that commonly correlate with patch-stack debt or weakened checks.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".java", ".kt", ".kts", ".go", ".rs", ".rb", ".php", ".cs", ".cpp",
    ".cc", ".cxx", ".c", ".h", ".hpp", ".swift", ".scala", ".vue", ".svelte",
    ".dart", ".ex", ".exs", ".lua", ".m", ".mm", ".sh", ".bash", ".zsh",
    ".fish", ".sql", ".html", ".htm", ".css", ".scss", ".sass", ".less",
}
EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", ".venv", "venv", "dist",
    "build", ".next", ".turbo", "coverage", "target", "out", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
GENERATED_HINTS = {"generated", "gen", "dist", "build", "vendor"}
TEST_HINTS = {"test", "tests", "spec", "specs", "__tests__"}

PATTERNS: list[tuple[str, str, str, re.Pattern[str]]] = [
    (
        "HIGH",
        "skipped-test",
        "Skipped/disabled test deserves justification",
        re.compile(
            r"(?:\.skip\s*\(|\bit\.skip\b|\btest\.skip\b|\bdescribe\.skip\b|"
            r"\bxit\s*\(|\bxtest\s*\(|\bxdescribe\s*\(|pytest\.mark\.(?:skip|xfail)|"
            r"@unittest\.(?:skip|skipIf|skipUnless))"
        ),
    ),
    (
        "HIGH",
        "focused-test",
        "Focused/only test can accidentally disable broader suite coverage",
        re.compile(r"(?:\.(?:only)\s*\(|\bfit\s*\(|\bfdescribe\s*\()"),
    ),
    ("HIGH", "empty-catch", "Empty catch block can silently hide failure", re.compile(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}", re.DOTALL)),
    (
        "WARN",
        "type-suppression",
        "Type-check suppression should be narrow and justified",
        re.compile(r"@ts-(?:ignore|nocheck|expect-error)|#\s*type:\s*ignore\b|pyright:\s*ignore"),
    ),
    ("WARN", "lint-suppression", "Lint suppression should be narrow and justified", re.compile(r"eslint-disable|ruff:\s*noqa|#\s*noqa\b")),
    ("WARN", "typescript-any", "New/broad TypeScript any can hide contract problems", re.compile(r"(?::|\bas)\s*any\b")),
    ("WARN", "debugger", "Debugger breakpoint may be temporary residue", re.compile(r"\bdebugger\s*;|\bbreakpoint\s*\(\s*\)|\bpdb\.set_trace\s*\(")),
    ("INFO", "todo-fixme", "TODO/FIXME may represent unfinished required behavior", re.compile(r"\b(?:TODO|FIXME|HACK)\b", re.IGNORECASE)),
    ("INFO", "debug-log", "Debug logging may be temporary residue", re.compile(r"\bconsole\.(?:log|debug)\s*\(")),
]

SEVERITY_RANK = {"INFO": 1, "WARN": 2, "HIGH": 3}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int | None
    message: str


def is_generated(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return bool(lowered & GENERATED_HINTS) or path.name.endswith((".generated.ts", ".generated.js", "_pb2.py"))


def is_test(path: Path) -> bool:
    lower_parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    return bool(lower_parts & TEST_HINTS) or any(marker in name for marker in (".test.", ".spec.", "_test.", "test_"))


def is_excluded(rel: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def iter_source_files(root: Path, exclude_patterns: tuple[str, ...] = ()):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        if is_excluded(rel, exclude_patterns):
            continue
        yield path


def first_line_number(text: str, match_start: int) -> int:
    return text.count("\n", 0, match_start) + 1


def audit_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return [Finding("WARN", "unreadable", rel, None, "Could not read file as UTF-8")]

    line_count = text.count("\n") + (1 if text else 0)
    if not is_generated(path):
        warn_limit, high_limit = ((900, 1500) if is_test(path) else (500, 800))
        if line_count > high_limit:
            findings.append(Finding("HIGH", "large-file", rel, None, f"{line_count} lines; inspect for mixed responsibilities (threshold {high_limit})"))
        elif line_count > warn_limit:
            findings.append(Finding("WARN", "large-file", rel, None, f"{line_count} lines; review whether responsibilities are still cohesive (threshold {warn_limit})"))

    for severity, code, message, pattern in PATTERNS:
        # Generated code can legitimately contain tool-produced suppressions.
        if is_generated(path) and code in {"type-suppression", "lint-suppression", "typescript-any"}:
            continue
        for match in pattern.finditer(text):
            findings.append(Finding(severity, code, rel, first_line_number(text, match.start()), message))

    return findings


def audit(root: Path, exclude_patterns: tuple[str, ...] = ()) -> list[Finding]:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"project root is not a directory: {root}")
    findings: list[Finding] = []
    for path in iter_source_files(root, exclude_patterns):
        findings.extend(audit_file(path, root))
    return sorted(findings, key=lambda f: (-SEVERITY_RANK[f.severity], f.path, f.line or 0, f.code))


def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "[OK] No heuristic findings"
    lines: list[str] = []
    for item in findings:
        location = f"{item.path}:{item.line}" if item.line else item.path
        lines.append(f"[{item.severity}] {item.code} {location} - {item.message}")
    counts = {level: sum(1 for f in findings if f.severity == level) for level in ("HIGH", "WARN", "INFO")}
    lines.append(f"Summary: {counts['HIGH']} high, {counts['WARN']} warning, {counts['INFO']} info")
    return "\n".join(lines)


def should_fail(findings: list[Finding], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = {"info": 1, "warn": 2, "high": 3}[fail_on]
    return any(SEVERITY_RANK[f.severity] >= threshold for f in findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Heuristically audit source structure and common quality bypasses.")
    parser.add_argument("root", nargs="?", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="Exclude a repository-relative glob; repeat as needed")
    parser.add_argument("--fail-on", choices=("none", "info", "warn", "high"), default="none", help="Exit non-zero at or above this severity")
    args = parser.parse_args(argv)

    root = Path(args.root)
    try:
        findings = audit(root, tuple(args.exclude))
    except (FileNotFoundError, NotADirectoryError) as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "findings": []}, indent=2))
        else:
            print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"findings": [asdict(f) for f in findings]}, indent=2))
    else:
        print(render_text(findings))
    return 1 if should_fail(findings, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
