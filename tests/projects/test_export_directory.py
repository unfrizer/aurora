"""P1-003 acceptance for the read-only project export-directory boundary."""

from __future__ import annotations

import json
import os
import shutil
import stat
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest

from src.core.exceptions import ValidationError
from src.projects import ProjectDocument, ProjectRepository


def _project_path(root: Path) -> Path:
    return next(root.iterdir())


def test_created_reopened_and_renamed_project_has_same_export_directory(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("First", {"keep": "state"})
    project = _project_path(tmp_path)
    exports = project / "exports"
    (exports / "prior.txt").write_text("preserve", encoding="utf-8")
    asset = repository.write_asset(
        original.metadata.project_id, b"GIF89a\x00\x00\x00\x00", "image/gif"
    )
    asset_before = (project / asset).read_bytes()
    metadata_before = (project / "aurora.project.json").read_bytes()
    state_before = (project / "state.json").read_bytes()

    assert repository.export_directory(original.metadata.project_id) == exports
    assert exports.is_absolute()
    assert ProjectRepository(tmp_path).export_directory(original.metadata.project_id) == exports
    assert (project / "aurora.project.json").read_bytes() == metadata_before
    assert (project / "state.json").read_bytes() == state_before
    assert (project / asset).read_bytes() == asset_before
    assert (exports / "prior.txt").read_text(encoding="utf-8") == "preserve"

    renamed = repository.save(
        ProjectDocument(metadata=replace(original.metadata, name="Second"), state=original.state)
    )
    assert ProjectRepository(tmp_path).export_directory(renamed.metadata.project_id) == exports
    assert (project / asset).read_bytes() == asset_before
    assert list(exports.iterdir()) == [exports / "prior.txt"]


@pytest.mark.parametrize("invalid", ["", "../project", "not-a-uuid"])
def test_malformed_identity_is_rejected_without_mutation(tmp_path: Path, invalid: str) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Safe")
    with pytest.raises(ValidationError, match="UUID"):
        repository.export_directory(invalid)
    assert repository.load(original.metadata.project_id) == original


def test_missing_and_duplicate_project_identity(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    with pytest.raises(FileNotFoundError):
        repository.export_directory(str(uuid4()))
    original = repository.create("One")
    project = _project_path(tmp_path)
    shutil.copytree(project, tmp_path / f"copy-{original.metadata.project_id}")
    with pytest.raises(ValidationError, match="Multiple"):
        repository.export_directory(original.metadata.project_id)
    assert (project / "exports").is_dir()


def test_corrupt_project_metadata_is_rejected_before_export_path(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One")
    metadata_path = _project_path(tmp_path) / "aurora.project.json"
    metadata = cast(dict[str, object], json.loads(metadata_path.read_text(encoding="utf-8")))
    metadata["format_version"] = "unsupported"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValidationError, match="format"):
        repository.export_directory(original.metadata.project_id)


@pytest.mark.parametrize("replacement", ["missing", "file"])
def test_missing_or_nondirectory_export_child_is_rejected(tmp_path: Path, replacement: str) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One")
    exports = _project_path(tmp_path) / "exports"
    exports.rmdir()
    if replacement == "file":
        exports.write_bytes(b"not a directory")
    with pytest.raises(ValidationError, match=r"^Invalid project export directory\.$"):
        repository.export_directory(original.metadata.project_id)
    assert exports.exists() is (replacement == "file")


@pytest.mark.parametrize("link_method", ["is_symlink", "is_junction"])
def test_linked_export_child_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, link_method: str
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One")
    exports = _project_path(tmp_path) / "exports"
    original_check = getattr(Path, link_method)

    def linked(path: Path) -> bool:
        return path == exports or cast(bool, original_check(path))

    monkeypatch.setattr(Path, link_method, linked)
    with pytest.raises(ValidationError, match=r"^Invalid project export directory\.$"):
        repository.export_directory(original.metadata.project_id)
    assert exports.is_dir()


def test_reparse_export_child_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One")
    exports = _project_path(tmp_path) / "exports"
    original_lstat = Path.lstat

    def reparse_lstat(path: Path) -> os.stat_result:
        details = original_lstat(path)
        if path == exports:
            return cast(
                os.stat_result,
                SimpleNamespace(
                    st_mode=details.st_mode,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
                ),
            )
        return details

    monkeypatch.setattr(Path, "lstat", reparse_lstat)
    with pytest.raises(ValidationError, match=r"^Invalid project export directory\.$"):
        repository.export_directory(original.metadata.project_id)


def test_linked_project_is_rejected_before_export_lookup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One")
    project = _project_path(tmp_path)
    original_check = Path.is_junction

    def linked(path: Path) -> bool:
        return path == project or original_check(path)

    monkeypatch.setattr(Path, "is_junction", linked)
    with pytest.raises(ValidationError, match="direct directory"):
        repository.export_directory(original.metadata.project_id)


def test_native_export_directory_io_failure_propagates_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("One", {"keep": True})
    project = _project_path(tmp_path)
    exports = project / "exports"
    state_before = (project / "state.json").read_bytes()
    original_lstat = Path.lstat

    def denied(path: Path) -> os.stat_result:
        if path == exports:
            raise PermissionError("simulated denial")
        return original_lstat(path)

    monkeypatch.setattr(Path, "lstat", denied)
    with pytest.raises(PermissionError, match="simulated denial"):
        repository.export_directory(original.metadata.project_id)
    assert (project / "state.json").read_bytes() == state_before
    assert not list(exports.iterdir())
