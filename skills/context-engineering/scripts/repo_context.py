#!/usr/bin/env python3
"""Build a compact deterministic repository-context map.

The script deliberately reports paths, versions and likely commands rather than
embedding file contents. It is a starting map for an agent, not a repository dump.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

INSTRUCTION_NAMES = {
    "AGENTS.md", "CLAUDE.md", ".cursorrules", "copilot-instructions.md",
}
MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml",
    "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
}
EXCLUDED_DIRS = {".git", "node_modules", "vendor", ".venv", "venv", "dist", "build", ".next", "target", "__pycache__"}
TEST_MARKERS = ("test", "tests", "spec", "specs", "__tests__")


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        yield path


def _git_changed(root: Path) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    out: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            out.append(line[3:].split(" -> ")[-1])
    return sorted(set(out))


def _instruction_files(root: Path) -> list[str]:
    found: list[str] = []
    for path in _iter_files(root):
        name = path.name
        rel = path.relative_to(root).as_posix()
        if name in INSTRUCTION_NAMES or rel == ".github/copilot-instructions.md" or rel.startswith(".cursor/rules/"):
            found.append(rel)
    return sorted(found)


def _manifest_info(root: Path) -> tuple[list[str], dict[str, str], list[str]]:
    manifests: list[str] = []
    versions: dict[str, str] = {}
    commands: list[str] = []
    package = root / "package.json"
    if package.is_file():
        manifests.append("package.json")
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            engines = data.get("engines", {}) if isinstance(data, dict) else {}
            if isinstance(engines, dict):
                for key, value in engines.items():
                    if isinstance(value, str):
                        versions[key] = value
            deps = {}
            for key in ("dependencies", "devDependencies"):
                section = data.get(key, {}) if isinstance(data, dict) else {}
                if isinstance(section, dict): deps.update(section)
            for key in ("next", "react", "typescript", "vite", "express"):
                if key in deps and isinstance(deps[key], str): versions[key] = deps[key]
            scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
            if isinstance(scripts, dict):
                for key in ("test", "typecheck", "lint", "build"):
                    if key in scripts: commands.append(f"npm run {key}")
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        manifests.append("pyproject.toml")
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"requires-python\s*=\s*[\"']([^\"']+)", text)
        if match: versions["python"] = match.group(1)
        commands.extend(["python -m unittest discover", "python -m pytest"])
    req = root / "requirements.txt"
    if req.is_file(): manifests.append("requirements.txt")
    cargo = root / "Cargo.toml"
    if cargo.is_file():
        manifests.append("Cargo.toml"); commands.extend(["cargo test", "cargo check"])
    gomod = root / "go.mod"
    if gomod.is_file():
        manifests.append("go.mod")
        text = gomod.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^go\s+([^\s]+)", text, re.MULTILINE)
        if match: versions["go"] = match.group(1)
        commands.append("go test ./...")
    return sorted(set(manifests)), versions, sorted(set(commands))


def _nearby(root: Path, target: Path | None, max_items: int = 12) -> tuple[list[str], list[str]]:
    if target is None:
        return [], []
    target = target.resolve()
    anchor = target if target.is_dir() else target.parent
    try:
        anchor.relative_to(root.resolve())
    except ValueError:
        return [], []
    files: list[str] = []
    tests: list[str] = []
    for path in _iter_files(anchor):
        rel = _rel(path, root)
        lower = rel.lower()
        if any(marker in lower.split("/") for marker in TEST_MARKERS) or ".test." in lower or ".spec." in lower or path.name.startswith("test_") or path.name.endswith("_test.py"):
            tests.append(rel)
        else:
            files.append(rel)
    return sorted(files)[:max_items], sorted(tests)[:max_items]


def build_context(root: Path, target: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")
    manifests, versions, commands = _manifest_info(root)
    nearby, tests = _nearby(root, target)
    top = sorted(p.name for p in root.iterdir() if p.is_dir() and p.name not in EXCLUDED_DIRS)[:30]
    return {
        "root": str(root),
        "target": None if target is None else str(target),
        "instructions": _instruction_files(root),
        "manifests": manifests,
        "versions": versions,
        "likely_commands": commands,
        "top_level_directories": top,
        "nearby_source": nearby,
        "nearby_tests": tests,
        "working_tree_changes": _git_changed(root),
    }


def render_text(data: dict[str, Any]) -> str:
    lines = ["Repository Context", "==================", f"Root: {data['root']}"]
    if data.get("target"): lines.append(f"Target: {data['target']}")
    sections = [
        ("Applicable instructions", data["instructions"]),
        ("Manifests", data["manifests"]),
        ("Top-level directories", data["top_level_directories"]),
        ("Nearby source", data["nearby_source"]),
        ("Nearby tests", data["nearby_tests"]),
        ("Likely verification commands", data["likely_commands"]),
        ("Working-tree changes", data["working_tree_changes"]),
    ]
    if data["versions"]:
        lines += ["", "Detected versions"] + [f"- {k}: {v}" for k, v in sorted(data["versions"].items())]
    for title, values in sections:
        lines += ["", title]
        lines += [f"- {v}" for v in values] if values else ["- (none detected)"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a compact repository-context map.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--target", type=Path, default=None, help="Optional file/directory to find nearby source/tests")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    target = None if args.target is None else (args.target if args.target.is_absolute() else root / args.target)
    try:
        data = build_context(root, target)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr); return 2
    text = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.json else render_text(data)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"[OK] Wrote {args.output}")
    else: sys.stdout.write(text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
