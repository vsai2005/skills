#!/usr/bin/env python3
"""Build a deterministic Google Antigravity plugin bundle from canonical skills."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

try:
    from scripts.package_release import ZIP_TIMESTAMP, read_version, require_no_pending_tests
    from scripts.release_common import iter_release_files, sha256_file
except ModuleNotFoundError:  # direct script execution from scripts/
    from package_release import ZIP_TIMESTAMP, read_version, require_no_pending_tests
    from release_common import iter_release_files, sha256_file


ANTIGRAVITY_SCHEMA = "https://antigravity.google/schemas/v1/plugin.json"
PLUGIN_NAME = "engineering-quality"
PLUGIN_DESCRIPTION = (
    "General engineering quality Agent Skills for building, debugging, refactoring, "
    "testing, security review, writing, and cross-layer project audits."
)


def _skill_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in iter_release_files(root):
        rel = path.relative_to(root)
        if len(rel.parts) >= 3 and rel.parts[0] == "skills":
            files.append(path)
    if not files:
        raise ValueError("no skill files found")
    return files


def _manifest() -> dict[str, str]:
    # Antigravity's plugin schema currently rejects additional manifest fields.
    return {
        "$schema": ANTIGRAVITY_SCHEMA,
        "name": PLUGIN_NAME,
        "description": PLUGIN_DESCRIPTION,
    }


def write_antigravity_plugin(root: Path, output_dir: Path) -> tuple[Path, Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if not root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")

    require_no_pending_tests(root)
    version = read_version(root)
    files = _skill_files(root)

    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_name = f"engineering-quality-antigravity-plugin-v{version}"
    stage_dir = output_dir / bundle_name
    zip_path = output_dir / f"{bundle_name}.zip"
    checksum_path = output_dir / f"{bundle_name}.sha256"

    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)
    manifest_path = stage_dir / "plugin.json"
    manifest_path.write_text(
        json.dumps(_manifest(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    for source in files:
        rel = source.relative_to(root)
        target = stage_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    if zip_path.exists():
        zip_path.unlink()

    bundle_files = [p for p in stage_dir.rglob("*") if p.is_file()]
    bundle_files.sort(key=lambda p: p.relative_to(stage_dir).as_posix())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in bundle_files:
            if path.is_symlink():
                raise ValueError(f"Antigravity bundle contains symlink: {path}")
            rel = path.relative_to(stage_dir).as_posix()
            info = zipfile.ZipInfo(f"{bundle_name}/{rel}", ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o100755 if path.stat().st_mode & 0o111 else 0o100644
            info.external_attr = (mode & 0xFFFF) << 16
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

    checksum = sha256_file(zip_path)
    checksum_path.write_text(f"{checksum}  {zip_path.name}\n", encoding="utf-8", newline="\n")
    return stage_dir, zip_path, checksum_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package the canonical skills as a Google Antigravity plugin."
    )
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--output-dir", default="dist", help="Output directory (default: dist)")
    args = parser.parse_args(argv)

    try:
        stage, zip_path, checksum = write_antigravity_plugin(
            Path(args.root), Path(args.output_dir)
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(f"[OK] Antigravity plugin directory: {stage}")
    print(f"[OK] Antigravity plugin ZIP: {zip_path}")
    print(f"[OK] SHA256: {checksum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
