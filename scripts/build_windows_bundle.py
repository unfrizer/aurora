"""Build a portable Windows AURORA ZIP from locked source dependencies."""

from __future__ import annotations

import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

_LOG = logging.getLogger("aurora.packaging")
_ROOT = Path(__file__).resolve().parents[1]
_ASSET_NAME = re.compile(r"[A-Za-z0-9._-]+\.(?:js|css|png|jpg|jpeg|gif|webp|ico|woff|woff2)\Z")
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _is_link(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)) or (
        path.is_symlink() or path.is_junction()
    )


def _regular_file(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except OSError:
        return False
    return stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1 and not _is_link(path)


def _safe_ancestors(path: Path) -> bool:
    return not any(_is_link(parent) for parent in (path, *path.parents))


def validate_frontend_bundle(root: Path) -> None:
    """Reject absent, linked, nested or unsupported Vite build outputs."""
    assets = root / "assets"
    if not root.is_dir() or not assets.is_dir() or not _safe_ancestors(assets):
        raise ValueError("The built frontend is missing or unsafe.")
    if not _regular_file(root / "index.html"):
        raise ValueError("The built frontend index is missing or unsafe.")
    if {child.name for child in root.iterdir()} != {"index.html", "assets"}:
        raise ValueError("The built frontend contains unexpected root files.")
    asset_files = list(assets.iterdir())
    if not asset_files:
        raise ValueError("The built frontend contains no assets.")
    for asset in asset_files:
        if _ASSET_NAME.fullmatch(asset.name) is None or not _regular_file(asset):
            raise ValueError("The built frontend contains an unsafe asset.")


def validate_frozen_bundle(root: Path) -> None:
    """Verify the one-folder executable and launcher-relative UI location."""
    if not root.is_dir() or not _safe_ancestors(root):
        raise ValueError("The frozen application directory is missing or unsafe.")
    if {child.name for child in root.iterdir()} != {"AURORA.exe", "_internal"}:
        raise ValueError("The frozen application has an unexpected top-level layout.")
    executable = root / "AURORA.exe"
    if not _regular_file(executable) or executable.stat().st_size == 0:
        raise ValueError("The frozen executable is missing or empty.")
    validate_frontend_bundle(root / "_internal" / "frontend" / "dist")
    for member in root.rglob("*"):
        if _is_link(member) or (not member.is_dir() and not _regular_file(member)):
            raise ValueError("The frozen application contains an unsafe member.")


def write_archive(bundle: Path, destination: Path) -> None:
    """Atomically replace only the generated ZIP after a complete validation."""
    validate_frozen_bundle(bundle)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not _safe_ancestors(destination.parent):
        raise ValueError("The archive destination is linked or unsafe.")
    if destination.exists() and not _regular_file(destination):
        raise ValueError("The archive destination is not a regular file.")
    handle, temporary_name = tempfile.mkstemp(
        prefix=".aurora-portable-", suffix=".zip", dir=destination.parent
    )
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for member in sorted(
                (path for path in bundle.rglob("*") if path.is_file()),
                key=lambda path: path.relative_to(bundle).as_posix(),
            ):
                relative = member.relative_to(bundle)
                entry = zipfile.ZipInfo(f"AURORA/{relative.as_posix()}", _ZIP_DATE)
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                with member.open("rb") as source, archive.open(entry, "w") as target:
                    shutil.copyfileobj(source, target)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    """Build the client, freeze the launcher, then write its portable ZIP."""
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        _LOG.error("Portable AURORA builds require Windows x64.")
        return 1
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        _LOG.error("pnpm 11 is required to build the AURORA frontend.")
        return 1
    frontend = _ROOT / "frontend"
    subprocess.run([pnpm, "install", "--frozen-lockfile"], cwd=frontend, check=True)
    subprocess.run([pnpm, "build"], cwd=frontend, check=True)
    validate_frontend_bundle(frontend / "dist")
    temporary_parent = _ROOT / "build" / "tmp"
    temporary_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aurora-pkg-", dir=temporary_parent) as temporary_name:
        temporary = Path(temporary_name)
        if not temporary.resolve().is_relative_to(temporary_parent.resolve()):
            raise RuntimeError("The package workspace is outside the repository build directory.")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--distpath",
                str(temporary / "dist"),
                "--workpath",
                str(temporary / "work"),
                str(_ROOT / "packaging" / "AURORA.spec"),
            ],
            cwd=_ROOT,
            check=True,
        )
        bundle = temporary / "dist" / "AURORA"
        destination = _ROOT / "build" / "portable" / "AURORA-Windows-x64.zip"
        write_archive(bundle, destination)
    _LOG.info("Portable AURORA archive ready: %s", destination)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
