#!/usr/bin/env python3
"""Generate FILE_MANIFEST.txt for release files.

The manifest intentionally excludes itself because a cryptographic hash of a
file cannot contain its own final hash without a circular definition.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from scripts.release_common import iter_release_files, sha256_file
except ModuleNotFoundError:  # direct script execution from scripts/
    from release_common import iter_release_files, sha256_file

HEADER = (
    "# FILE_MANIFEST v1\n"
    "# Columns: sha256<TAB>bytes<TAB>repository-relative path\n"
    "# FILE_MANIFEST.txt and transient cache/VCS files are intentionally excluded.\n"
)


def build_manifest(root: Path) -> str:
    root = root.resolve()
    lines = [HEADER.rstrip("\n")]
    for path in iter_release_files(root):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{sha256_file(path)}\t{path.stat().st_size}\t{rel}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic release file manifest.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Verify existing manifest instead of writing it")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[ERROR] repository root is not a directory: {root}", file=sys.stderr)
        return 2

    path = root / "FILE_MANIFEST.txt"
    expected = build_manifest(root)
    if args.check:
        if not path.is_file():
            print("[ERROR] FILE_MANIFEST.txt is missing", file=sys.stderr)
            return 1
        try:
            current = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"[ERROR] cannot read FILE_MANIFEST.txt: {exc}", file=sys.stderr)
            return 1
        if current != expected:
            print("[ERROR] FILE_MANIFEST.txt is stale or inconsistent", file=sys.stderr)
            return 1
        print("[OK] FILE_MANIFEST.txt matches release files")
        return 0

    path.write_text(expected, encoding="utf-8", newline="\n")
    print(f"[OK] Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
