#!/usr/bin/env python3
"""Create a deterministic ZIP release and portable SHA-256 checksum file."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

try:
    from scripts.generate_manifest import build_manifest
    from scripts.release_common import iter_release_files, sha256_file
except ModuleNotFoundError:  # direct script execution from scripts/
    from generate_manifest import build_manifest
    from release_common import iter_release_files, sha256_file

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def read_version(root: Path) -> str:
    path = root / "VERSION"
    if not path.is_file():
        raise ValueError("VERSION is missing")
    version = path.read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("VERSION is empty")
    return version


def require_no_pending_tests(root: Path) -> None:
    """Block a release while any managed deferred verification remains."""
    pending = root / "PENDING_TESTS.md"
    if not pending.exists():
        return
    try:
        from scripts.pending_tests import load_items
    except ModuleNotFoundError:
        from pending_tests import load_items
    items = load_items(pending)
    if items:
        ids = ", ".join(item.id for item in items)
        raise ValueError(f"release blocked by {len(items)} pending test(s): {ids}")


def write_release(root: Path, output_dir: Path, archive_root: str = "engineering-quality-agent-skills") -> tuple[Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    require_no_pending_tests(root)

    manifest_path = root / "FILE_MANIFEST.txt"
    manifest_path.write_text(build_manifest(root), encoding="utf-8", newline="\n")

    version = read_version(root)
    zip_path = output_dir / f"engineering-quality-agent-skills-v{version}.zip"
    checksum_path = output_dir / f"engineering-quality-agent-skills-v{version}.sha256"

    files = list(iter_release_files(root)) + [manifest_path]
    files.sort(key=lambda p: p.relative_to(root).as_posix())

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            # iter_release_files already rejects symlinks/sensitive files. The
            # explicit recheck prevents a race from swapping a path afterward.
            if path.is_symlink():
                raise ValueError(f"release candidate became a symlink: {path.relative_to(root).as_posix()}")
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{archive_root}/{rel}", ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o100755 if path.stat().st_mode & 0o111 else 0o100644
            info.external_attr = (mode & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    checksum = sha256_file(zip_path)
    checksum_path.write_text(f"{checksum}  {zip_path.name}\n", encoding="utf-8", newline="\n")
    return zip_path, checksum_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package a deterministic engineering-quality skill release.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--output-dir", default="dist", help="Output directory (default: dist)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"[ERROR] repository root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        zip_path, checksum_path = write_release(root, Path(args.output_dir))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] ZIP: {zip_path}")
    print(f"[OK] SHA256: {checksum_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
