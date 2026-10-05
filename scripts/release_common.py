#!/usr/bin/env python3
"""Shared release-file helpers used by validation and packaging."""

from __future__ import annotations

import hashlib
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
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    "FILE_MANIFEST.txt",  # self-reference is intentionally excluded
}

EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def is_release_file(path: Path, root: Path) -> bool:
    """Return whether *path* belongs in a source release."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if not path.is_file():
        return False
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts[:-1]):
        return False
    if path.name in EXCLUDED_FILE_NAMES:
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return True


def iter_release_files(root: Path) -> Iterator[Path]:
    """Yield release files in stable repository-relative order."""
    root = root.resolve()
    paths = [p for p in root.rglob("*") if is_release_file(p, root)]
    yield from sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
