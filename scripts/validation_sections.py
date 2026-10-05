"""Manifest, eval, and release-manifest validation sections."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.release_common import iter_release_files, sha256_file
except ModuleNotFoundError:  # direct script execution from scripts/
    from release_common import iter_release_files, sha256_file

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
EXPECTED_PLUGIN_NAME = "engineering-quality"


@dataclass(frozen=True)
class Problem:
    level: str
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        return f"[{self.level}] {rel}: {self.message}"


def read_json(path: Path) -> tuple[dict | list | None, Problem | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, Problem("ERROR", path, f"invalid JSON: {exc}")


def validate_skills_path(root: Path, manifest_path: Path, data: dict, *, required: bool) -> list[Problem]:
    raw = data.get("skills")
    if raw is None:
        return [Problem("ERROR", manifest_path, "manifest must declare the skills directory")] if required else []
    if not isinstance(raw, str) or not raw.strip():
        return [Problem("ERROR", manifest_path, "skills must be a non-empty relative path string")]
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return [Problem("ERROR", manifest_path, f"skills path escapes repository: {raw}")]
    if not candidate.is_dir():
        return [Problem("ERROR", manifest_path, f"skills path does not resolve to a directory: {raw}")]
    return []


def validate_manifests(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    version_path = root / "VERSION"
    release_version: str | None = None
    if not version_path.is_file():
        problems.append(Problem("ERROR", version_path, "VERSION file missing"))
    else:
        try:
            release_version = version_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as exc:
            problems.append(Problem("ERROR", version_path, f"cannot read VERSION: {exc}"))
        if release_version is not None and not SEMVER_RE.fullmatch(release_version):
            problems.append(Problem("ERROR", version_path, "VERSION must use simple semantic versioning, e.g. 1.0.1"))

    manifests: dict[str, dict] = {}
    for rel in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        path = root / rel
        if not path.is_file():
            problems.append(Problem("ERROR", path, "manifest missing"))
            continue
        data, error = read_json(path)
        if error:
            problems.append(error)
            continue
        if not isinstance(data, dict):
            problems.append(Problem("ERROR", path, "manifest root must be a JSON object"))
            continue
        manifests[rel] = data
        if data.get("name") != EXPECTED_PLUGIN_NAME:
            problems.append(Problem("ERROR", path, f"manifest name must be {EXPECTED_PLUGIN_NAME!r}"))
        version = data.get("version")
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            problems.append(Problem("ERROR", path, "manifest version must use simple semantic versioning"))
        elif release_version and version != release_version:
            problems.append(Problem("ERROR", path, f"manifest version {version} does not match VERSION {release_version}"))
        if not str(data.get("description", "")).strip():
            problems.append(Problem("ERROR", path, "manifest description must not be empty"))

    portable = manifests.get("plugin.json")
    if portable is not None:
        schema = portable.get("$schema")
        if not isinstance(schema, str) or "agent-plugins.org" not in schema:
            problems.append(Problem("ERROR", root / "plugin.json", "portable manifest must declare the Agent Plugins schema"))
        problems.extend(validate_skills_path(root, root / "plugin.json", portable, required=True))

    codex = manifests.get(".codex-plugin/plugin.json")
    if codex is not None:
        problems.extend(validate_skills_path(root, root / ".codex-plugin/plugin.json", codex, required=True))

    claude = manifests.get(".claude-plugin/plugin.json")
    if claude is not None:
        license_name = claude.get("license")
        if not isinstance(license_name, str) or not license_name.strip():
            problems.append(Problem("WARN", root / ".claude-plugin/plugin.json", "license metadata is missing"))
        keywords = claude.get("keywords")
        if keywords is not None and (
            not isinstance(keywords, list)
            or not all(isinstance(item, str) and item.strip() for item in keywords)
        ):
            problems.append(Problem("ERROR", root / ".claude-plugin/plugin.json", "keywords must be a list of non-empty strings"))

    versions = {
        rel: data.get("version")
        for rel, data in manifests.items()
        if isinstance(data.get("version"), str) and SEMVER_RE.fullmatch(data["version"])
    }
    if len(set(versions.values())) > 1:
        problems.append(Problem("ERROR", root, f"manifest versions disagree: {versions}"))
    return problems


def validate_activation_evals(root: Path, skill_names: set[str]) -> list[Problem]:
    path = root / "evals" / "activation-cases.json"
    if not path.is_file():
        return [Problem("ERROR", path, "activation eval file missing")]
    data, error = read_json(path)
    if error:
        return [error]
    if not isinstance(data, list) or not data:
        return [Problem("ERROR", path, "activation evals must be a non-empty JSON list")]

    problems: list[Problem] = []
    ids: set[str] = set()
    allowed = skill_names | {"none"}
    covered: set[str] = set()
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            problems.append(Problem("ERROR", path, f"case {index} must be an object"))
            continue
        case_id = str(case.get("id", "")).strip()
        prompt = str(case.get("prompt", "")).strip()
        expected = str(case.get("expected_primary_skill", "")).strip()
        if not case_id:
            problems.append(Problem("ERROR", path, f"case {index} has no id"))
        elif case_id in ids:
            problems.append(Problem("ERROR", path, f"duplicate case id: {case_id}"))
        ids.add(case_id)
        if not prompt:
            problems.append(Problem("ERROR", path, f"case {case_id or index} has empty prompt"))
        if expected not in allowed:
            problems.append(Problem("ERROR", path, f"case {case_id or index} expects unknown skill: {expected}"))
        elif expected != "none":
            covered.add(expected)

    missing = sorted(skill_names - covered)
    if missing:
        problems.append(Problem("ERROR", path, f"activation evals do not cover skill(s): {', '.join(missing)}"))
    if not any(isinstance(case, dict) and case.get("expected_primary_skill") == "none" for case in data):
        problems.append(Problem("ERROR", path, "activation evals need at least one negative/none case"))
    return problems


def validate_behavior_evals(root: Path, skill_names: set[str]) -> list[Problem]:
    path = root / "evals" / "behavior-cases.json"
    if not path.is_file():
        return [Problem("ERROR", path, "machine-readable behavior eval file missing")]
    data, error = read_json(path)
    if error:
        return [error]
    if not isinstance(data, list) or not data:
        return [Problem("ERROR", path, "behavior evals must be a non-empty JSON list")]

    problems: list[Problem] = []
    ids: set[str] = set()
    covered: set[str] = set()
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            problems.append(Problem("ERROR", path, f"case {index} must be an object"))
            continue
        case_id = str(case.get("id", "")).strip()
        request = str(case.get("request", "")).strip()
        fixture = str(case.get("fixture", "")).strip()
        skills = case.get("skills")
        expected = case.get("expected_behaviors")
        if not case_id:
            problems.append(Problem("ERROR", path, f"case {index} has no id"))
        elif case_id in ids:
            problems.append(Problem("ERROR", path, f"duplicate behavior case id: {case_id}"))
        ids.add(case_id)
        if not request:
            problems.append(Problem("ERROR", path, f"case {case_id or index} has empty request"))
        if not fixture:
            problems.append(Problem("ERROR", path, f"case {case_id or index} has empty fixture"))
        if not isinstance(skills, list) or not skills:
            problems.append(Problem("ERROR", path, f"case {case_id or index} must list one or more skills"))
        else:
            for skill in skills:
                if skill not in skill_names:
                    problems.append(Problem("ERROR", path, f"case {case_id or index} names unknown skill: {skill}"))
                else:
                    covered.add(skill)
        if not isinstance(expected, list) or len(expected) < 2 or not all(isinstance(item, str) and item.strip() for item in expected):
            problems.append(Problem("ERROR", path, f"case {case_id or index} needs at least two non-empty expected_behaviors"))

    missing = sorted(skill_names - covered)
    if missing:
        problems.append(Problem("ERROR", path, f"behavior evals do not cover skill(s): {', '.join(missing)}"))
    return problems


def validate_evals(root: Path, skill_names: set[str]) -> list[Problem]:
    return validate_activation_evals(root, skill_names) + validate_behavior_evals(root, skill_names)


def validate_file_manifest(root: Path) -> list[Problem]:
    path = root / "FILE_MANIFEST.txt"
    if not path.is_file():
        return [Problem("ERROR", path, "release file manifest missing")]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [Problem("ERROR", path, f"cannot read manifest: {exc}")]

    problems: list[Problem] = []
    actual: dict[str, tuple[str, int]] = {}
    for index, line in enumerate(lines, start=1):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            problems.append(Problem("ERROR", path, f"invalid manifest row at line {index}"))
            continue
        digest, size_raw, rel = parts
        if rel in actual:
            problems.append(Problem("ERROR", path, f"duplicate manifest path: {rel}"))
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            problems.append(Problem("ERROR", path, f"invalid SHA-256 for {rel}"))
            continue
        try:
            size = int(size_raw)
        except ValueError:
            problems.append(Problem("ERROR", path, f"invalid byte size for {rel}"))
            continue
        actual[rel] = (digest, size)

    expected_paths = {p.relative_to(root).as_posix(): p for p in iter_release_files(root)}
    actual_paths = set(actual)
    for rel in sorted(set(expected_paths) - actual_paths):
        problems.append(Problem("ERROR", path, f"manifest missing release file: {rel}"))
    for rel in sorted(actual_paths - set(expected_paths)):
        problems.append(Problem("ERROR", path, f"manifest lists non-release/missing file: {rel}"))

    for rel in sorted(actual_paths & set(expected_paths)):
        target = expected_paths[rel]
        digest, size = actual[rel]
        current_size = target.stat().st_size
        if size != current_size:
            problems.append(Problem("ERROR", path, f"size mismatch for {rel}: manifest {size}, actual {current_size}"))
        if digest != sha256_file(target):
            problems.append(Problem("ERROR", path, f"SHA-256 mismatch for {rel}"))
    return problems
