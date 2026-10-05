#!/usr/bin/env python3
"""Validate structure, metadata, evals, manifests, links, and release integrity."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from scripts.validation_sections import (
        Problem,
        validate_evals,
        validate_file_manifest,
        validate_manifests,
    )
except ModuleNotFoundError:  # direct script execution from scripts/
    from validation_sections import Problem, validate_evals, validate_file_manifest, validate_manifests

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
OPENAI_FIELD_RE = re.compile(r'^\s{2}(display_name|short_description|default_prompt):\s+"(.*)"\s*$')


def parse_minimal_frontmatter(skill_md: Path) -> tuple[dict[str, str] | None, list[Problem]]:
    problems: list[Problem] = []
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, [Problem("ERROR", skill_md, f"cannot read UTF-8 text: {exc}")]

    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, [Problem("ERROR", skill_md, "missing or malformed YAML frontmatter")]

    data: dict[str, str] = {}
    for lineno, raw in enumerate(match.group(1).splitlines(), start=2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in raw:
            problems.append(Problem("ERROR", skill_md, f"invalid frontmatter line {lineno}"))
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            problems.append(Problem("ERROR", skill_md, f"frontmatter field {key!r} is empty"))
            continue
        if value.startswith(('"', "'")) and value.endswith(value[0]) and len(value) >= 2:
            value = value[1:-1]
        data[key] = value

    # Deliberately stricter than the open spec for maximum cross-host portability.
    allowed = {"name", "description"}
    extra = sorted(set(data) - allowed)
    missing = sorted(allowed - set(data))
    if extra:
        problems.append(Problem("ERROR", skill_md, f"unsupported frontmatter field(s): {', '.join(extra)}"))
    if missing:
        problems.append(Problem("ERROR", skill_md, f"missing required field(s): {', '.join(missing)}"))
    return data, problems


def markdown_targets(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    return MD_LINK_RE.findall(text)


def resolve_local_markdown_link(path: Path, target: str, root: Path) -> Path | None:
    target = target.strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = target.split("#", 1)[0].strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if not target:
        return None
    candidate = (path.parent / target).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate_skill_reachability(skill_dir: Path) -> list[Problem]:
    """Require Markdown references/assets to be reachable from SKILL.md."""
    entry = skill_dir / "SKILL.md"
    if not entry.is_file():
        return []

    resource_files: set[Path] = set()
    for folder_name in ("references", "assets"):
        folder = skill_dir / folder_name
        if folder.is_dir():
            resource_files.update(p.resolve() for p in folder.rglob("*.md") if p.is_file())
    if not resource_files:
        return []

    reachable: set[Path] = set()
    queue = [entry.resolve()]
    seen: set[Path] = set()
    while queue:
        current = queue.pop()
        if current in seen or not current.is_file():
            continue
        seen.add(current)
        for raw_target in markdown_targets(current):
            candidate = resolve_local_markdown_link(current, raw_target, skill_dir)
            if candidate is None or not candidate.is_file() or candidate.suffix.lower() != ".md":
                continue
            if candidate in resource_files and candidate not in reachable:
                reachable.add(candidate)
                queue.append(candidate)

    return [
        Problem("WARN", resource, "resource is not reachable from SKILL.md progressive-disclosure links")
        for resource in sorted(resource_files - reachable)
    ]


def validate_openai_yaml(path: Path, skill_name: str) -> list[Problem]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [Problem("ERROR", path, f"cannot read UTF-8 text: {exc}")]

    problems: list[Problem] = []
    if not text.startswith("interface:\n") and not text.startswith("interface:\r\n"):
        problems.append(Problem("ERROR", path, "must start with 'interface:'"))

    values: dict[str, str] = {}
    for raw in text.splitlines():
        match = OPENAI_FIELD_RE.match(raw)
        if match:
            values[match.group(1)] = match.group(2)

    for field in ("display_name", "short_description", "default_prompt"):
        if field not in values:
            problems.append(Problem("ERROR", path, f"missing quoted interface field {field}"))
    short = values.get("short_description", "")
    if short and not 25 <= len(short) <= 64:
        problems.append(Problem("ERROR", path, "short_description must be 25-64 characters"))
    prompt = values.get("default_prompt", "")
    if prompt and f"${skill_name}" not in prompt:
        problems.append(Problem("WARN", path, f"default_prompt does not name ${skill_name}"))
    return problems


def validate_skill(skill_dir: Path) -> list[Problem]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [Problem("ERROR", skill_dir, "SKILL.md not found")]

    data, problems = parse_minimal_frontmatter(skill_md)
    if not data:
        return problems
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if not name:
        problems.append(Problem("ERROR", skill_md, "name must not be empty"))
    elif len(name) > 64:
        problems.append(Problem("ERROR", skill_md, "name must be at most 64 characters"))
    elif not NAME_RE.fullmatch(name):
        problems.append(Problem("ERROR", skill_md, "name must use lowercase letters, digits, and hyphens"))
    if name and skill_dir.name != name:
        problems.append(Problem("ERROR", skill_md, f"folder name {skill_dir.name!r} must match skill name {name!r}"))
    if len(description) < 40:
        problems.append(Problem("ERROR", skill_md, "description is too short to provide reliable activation context"))
    if len(description) > 600:
        problems.append(Problem("WARN", skill_md, "description is unusually long; keep discovery metadata discriminating"))

    try:
        line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError):
        line_count = 0
    if line_count > 500:
        problems.append(Problem("WARN", skill_md, f"SKILL.md is {line_count} lines; prefer progressive disclosure below ~500 lines"))

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        problems.append(Problem("WARN", skill_dir, "agents/openai.yaml missing"))
    else:
        problems.extend(validate_openai_yaml(openai_yaml, name))
    problems.extend(validate_skill_reachability(skill_dir))
    return problems


def validate_markdown_links(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    resolved_root = root.resolve()
    for path in root.rglob("*.md"):
        if any(part in {".git", "node_modules", ".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.append(Problem("ERROR", path, f"cannot read UTF-8 text: {exc}"))
            continue
        for target in MD_LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0].strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(resolved_root)
            except ValueError:
                problems.append(Problem("ERROR", path, f"local link escapes repository: {target}"))
                continue
            if not candidate.exists():
                problems.append(Problem("ERROR", path, f"broken local link: {target}"))
    return problems


def validate_repo(root: Path) -> list[Problem]:
    root = root.resolve()
    if not root.is_dir():
        return [Problem("ERROR", root, "repository root does not exist or is not a directory")]

    problems = validate_manifests(root)
    skill_names: set[str] = set()
    skills_root = root / "skills"
    if not skills_root.is_dir():
        problems.append(Problem("ERROR", skills_root, "skills directory missing"))
    else:
        skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir())
        if not skill_dirs:
            problems.append(Problem("ERROR", skills_root, "no skills found"))
        for skill_dir in skill_dirs:
            skill_names.add(skill_dir.name)
            problems.extend(validate_skill(skill_dir))

    if skill_names:
        problems.extend(validate_evals(root, skill_names))
    problems.extend(validate_markdown_links(root))
    problems.extend(validate_file_manifest(root))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate engineering-quality skill repository metadata, evals, links, and release integrity.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Return failure when warnings are present")
    args = parser.parse_args(argv)

    root = Path(args.root)
    problems = validate_repo(root)
    errors = [p for p in problems if p.level == "ERROR"]
    warnings = [p for p in problems if p.level == "WARN"]
    for problem in problems:
        print(problem.render(root.resolve()))
    if not problems:
        print("[OK] Repository validation passed")
    else:
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors or (args.warnings_as_errors and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
