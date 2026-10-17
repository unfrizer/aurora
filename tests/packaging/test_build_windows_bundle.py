"""Portable bundle validation and deterministic ZIP tests."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from scripts.build_windows_bundle import (
    validate_frontend_bundle,
    validate_frozen_bundle,
    write_archive,
)


def _frontend(root: Path) -> Path:
    assets = root / "assets"
    assets.mkdir(parents=True)
    (root / "index.html").write_text("<html>AURORA</html>", encoding="utf-8")
    (assets / "app.js").write_text("export {};", encoding="utf-8")
    return root


def _frozen(root: Path) -> Path:
    root.mkdir()
    (root / "AURORA.exe").write_bytes(b"MZtest")
    (root / "_internal").mkdir()
    (root / "_internal" / "python313.dll").write_bytes(b"runtime")
    _frontend(root / "_internal" / "frontend" / "dist")
    return root


def test_frontend_bundle_accepts_only_launcher_supported_files(tmp_path: Path) -> None:
    root = _frontend(tmp_path / "frontend" / "dist")
    validate_frontend_bundle(root)
    (root / "assets" / "app.js.map").write_text("source", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe asset"):
        validate_frontend_bundle(root)


def test_frontend_bundle_rejects_missing_or_extra_root_files(tmp_path: Path) -> None:
    root = _frontend(tmp_path / "frontend" / "dist")
    (root / "favicon.ico").write_bytes(b"icon")
    with pytest.raises(ValueError, match="unexpected root"):
        validate_frontend_bundle(root)
    (root / "favicon.ico").unlink()
    (root / "index.html").unlink()
    with pytest.raises(ValueError, match="index"):
        validate_frontend_bundle(root)


def test_frontend_bundle_rejects_hardlinked_asset(tmp_path: Path) -> None:
    root = _frontend(tmp_path / "frontend" / "dist")
    source = tmp_path / "external.js"
    source.write_text("export {}", encoding="utf-8")
    os.link(source, root / "assets" / "other.js")
    with pytest.raises(ValueError, match="unsafe asset"):
        validate_frontend_bundle(root)


def test_frozen_bundle_rejects_extra_top_level_member(tmp_path: Path) -> None:
    root = _frozen(tmp_path / "AURORA")
    validate_frozen_bundle(root)
    (root / "state.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected top-level"):
        validate_frozen_bundle(root)


def test_archive_contains_only_portable_bundle_with_stable_names(tmp_path: Path) -> None:
    root = _frozen(tmp_path / "AURORA")
    destination = tmp_path / "artifacts" / "AURORA-Windows-x64.zip"
    write_archive(root, destination)
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        assert names == [
            "AURORA/AURORA.exe",
            "AURORA/_internal/frontend/dist/assets/app.js",
            "AURORA/_internal/frontend/dist/index.html",
            "AURORA/_internal/python313.dll",
        ]
        assert archive.read("AURORA/AURORA.exe") == b"MZtest"
        assert all(archive.getinfo(name).date_time == (1980, 1, 1, 0, 0, 0) for name in names)
    original = destination.read_bytes()
    write_archive(root, destination)
    assert destination.read_bytes() == original


def test_failed_validation_preserves_existing_archive(tmp_path: Path) -> None:
    root = _frozen(tmp_path / "AURORA")
    destination = tmp_path / "artifacts" / "AURORA-Windows-x64.zip"
    write_archive(root, destination)
    previous = destination.read_bytes()
    (root / "AURORA.exe").unlink()
    with pytest.raises(ValueError, match="top-level"):
        write_archive(root, destination)
    assert destination.read_bytes() == previous
