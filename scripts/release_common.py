#!/usr/bin/env python3
"""Shared release-file helpers used by validation and packaging.

Release selection is deliberately conservative:
- when a Git worktree is available, only Git-tracked files are candidates;
- source archives without Git fall back to a filesystem scan;
- symlinks and obvious secret-bearing filenames are rejected rather than followed;
- build/cache/verification output is excluded in both modes.
"""

from __future__ import annotations

import fnmatch
import hashlib
import subprocess
from pathlib import Path
from typing import Iterator

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".verification",
    "dist",
    "build",
    ".next",
    "coverage",
    "htmlcov",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    "FILE_MANIFEST.txt",  # self-reference is intentionally excluded
}

EXCLUDED_SUFFIXES = {".pyc", ".pyo"}

# These are release-deny patterns, not a complete secret scanner. They prevent
# the most common accidental credential files from entering a public archive.
SENSITIVE_NAME_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    ".npmrc",
    ".pypirc",
    "id_rsa",
    "id_ed25519",
    "credentials",
    "credentials.*",
    "secrets",
    "secrets.*",
)


def _relative(path: Path, root: Path) -> Path | None:
    try:
        return path.relative_to(root)
    except ValueError:
        return None


def is_sensitive_release_path(path: Path) -> bool:
    """Return whether the basename is unsafe for a public source release."""
    name = path.name.lower()
    return any(fnmatch.fnmatch(name, pattern.lower()) for pattern in SENSITIVE_NAME_PATTERNS)


def _excluded_by_location(rel: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in rel.parts[:-1])


def _validate_candidate(path: Path, root: Path) -> bool:
    """Validate one release candidate and return whether it should be included.

    Unsafe candidates raise instead of being silently skipped, because a tracked
    symlink or credential file is itself a release-integrity problem.
    """
    rel = _relative(path, root)
    if rel is None:
        return False
    if _excluded_by_location(rel):
        return False
    if path.name in EXCLUDED_FILE_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if path.is_symlink():
        raise ValueError(f"release candidate is a symlink: {rel.as_posix()}")
    if is_sensitive_release_path(path):
        raise ValueError(f"sensitive filename is not allowed in release: {rel.as_posix()}")
    if not path.is_file():
        return False
    return True


def _git_tracked_paths(root: Path) -> list[Path] | None:
    """Return tracked paths when *root* is the Git top-level, else None.

    A source ZIP intentionally has no .git directory, so callers can fall back
    to a secure filesystem scan in that case.
    """
    top = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if top.returncode != 0:
        return None
    git_root = Path(top.stdout.strip()).resolve()
    if git_root != root.resolve():
        raise ValueError(f"release root must be the Git top-level: {git_root}")
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if listed.returncode != 0:
        raise ValueError(listed.stderr.decode("utf-8", "replace").strip() or "git ls-files failed")
    result: list[Path] = []
    for raw in listed.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", "surrogateescape")
        result.append(root / rel)
    return result


def release_uses_git_tracking(root: Path) -> bool:
    """Return whether release selection can be bound to Git-tracked paths."""
    return _git_tracked_paths(root.resolve()) is not None


def is_release_file(path: Path, root: Path) -> bool:
    """Return whether *path* is a safe source-release file candidate."""
    return _validate_candidate(path, root.resolve())


def iter_release_files(root: Path) -> Iterator[Path]:
    """Yield safe release files in stable repository-relative order.

    Git worktrees package tracked files only. Source archives without Git use a
    filesystem scan, but still reject symlinks and sensitive filenames. Keep the
    caller's absolute path spelling instead of resolving it so Windows 8.3 short
    paths and their long-path aliases do not make yielded paths unusable with
    ``Path.relative_to(caller_root)``. Security comparisons still resolve paths
    inside ``_git_tracked_paths`` where canonical identity matters.
    """
    root = root.absolute()
    tracked = _git_tracked_paths(root)
    if tracked is not None:
        for path in tracked:
            if not path.exists() and not path.is_symlink():
                raise ValueError(
                    f"tracked release path is missing from worktree: {path.relative_to(root).as_posix()}"
                )
        candidates = tracked
    else:
        candidates = [p for p in root.rglob("*")]
    paths = [p for p in candidates if _validate_candidate(p, root)]
    yield from sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
