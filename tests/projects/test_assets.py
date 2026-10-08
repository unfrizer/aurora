"""P1-002 acceptance for bounded project-owned raster bytes."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Literal, cast
from uuid import uuid4

import pytest

from src.core.exceptions import ValidationError
from src.projects import ProjectDocument, ProjectRepository

MediaType = Literal["image/png", "image/jpeg", "image/gif", "image/webp"]
_SIGNATURES: dict[MediaType, bytes] = {
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
    "image/gif": b"GIF89a",
    "image/webp": b"RIFF\x00\x00\x00\x00WEBP",
}
_EXTENSIONS: dict[MediaType, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}


def _project_path(root: Path) -> Path:
    return next(root.iterdir())


def _raster(media_type: MediaType, suffix: bytes = b"test") -> bytes:
    return _SIGNATURES[media_type] + suffix


@pytest.mark.parametrize("media_type", tuple(_SIGNATURES))
def test_all_raster_formats_have_deterministic_reopenable_references(
    tmp_path: Path, media_type: MediaType
) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    data = _raster(media_type)
    expected = f"assets/{hashlib.sha256(data).hexdigest()}.{_EXTENSIONS[media_type]}"

    assert repository.write_asset(project.metadata.project_id, data, media_type) == expected
    assert repository.write_asset(project.metadata.project_id, data, media_type) == expected
    reopened = ProjectRepository(tmp_path)
    assert reopened.read_asset(project.metadata.project_id, expected) == data
    assert list((_project_path(tmp_path) / "assets").iterdir()) == [
        _project_path(tmp_path) / expected
    ]


@pytest.mark.parametrize("media_type", tuple(_SIGNATURES))
def test_declared_media_type_must_match_signature(tmp_path: Path, media_type: MediaType) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    wrong = cast(MediaType, next(candidate for candidate in _SIGNATURES if candidate != media_type))

    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(project.metadata.project_id, _raster(wrong), media_type)
    assert not list((_project_path(tmp_path) / "assets").iterdir())


@pytest.mark.parametrize(
    "invalid",
    [
        "",
        "assets/x.png",
        "assets/" + "A" * 64 + ".png",
        "assets/" + "a" * 64 + ".PNG",
        "assets/" + "a" * 64 + ".jpeg",
        "assets/../state.json",
        "assets\\file.png",
        "/assets/" + "a" * 64 + ".png",
        "C:/assets/" + "a" * 64 + ".png",
        "//server/assets/" + "a" * 64 + ".png",
        "https://example.test/assets/" + "a" * 64 + ".png",
        "assets/" + "a" * 64 + ".png:stream",
        "assets/" + "a" * 64 + ".png/extra",
    ],
)
def test_only_canonical_read_delete_paths_are_accepted(tmp_path: Path, invalid: str) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    for operation in (repository.read_asset, repository.delete_asset):
        with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
            operation(project.metadata.project_id, invalid)


def test_invalid_inputs_do_not_change_project_or_publish_assets(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster", {"keep": "untouched"})
    folder = _project_path(tmp_path)
    original_state = (folder / "state.json").read_bytes()
    original_metadata = (folder / "aurora.project.json").read_bytes()
    for data in (b"", b"x", _raster("image/png") + b"x" * (16 * 1024 * 1024)):
        with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
            repository.write_asset(project.metadata.project_id, data, "image/png")
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(
            project.metadata.project_id, _raster("image/png"), cast(MediaType, "image/bmp")
        )
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(
            project.metadata.project_id, cast(bytes, bytearray(_raster("image/png"))), "image/png"
        )
    assert not list((folder / "assets").iterdir())
    assert (folder / "state.json").read_bytes() == original_state
    assert (folder / "aurora.project.json").read_bytes() == original_metadata


def test_project_identity_isolation_and_missing_assets(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    first = repository.create("First")
    second = repository.create("Second")
    reference = repository.write_asset(first.metadata.project_id, _raster("image/png"), "image/png")

    with pytest.raises(FileNotFoundError, match="Project asset not found"):
        repository.read_asset(second.metadata.project_id, reference)
    assert repository.delete_asset(second.metadata.project_id, reference) is False
    with pytest.raises(FileNotFoundError, match="Project not found"):
        repository.read_asset(str(uuid4()), reference)
    assert repository.read_asset(first.metadata.project_id, reference) == _raster("image/png")


def test_unknown_entries_are_ignored_and_preserved(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    directory = _project_path(tmp_path) / "assets"
    note = directory / "notes.txt"
    orphan = directory / ".aurora-asset-old"
    note.write_bytes(b"keep")
    orphan.write_bytes(b"keep")

    reference = repository.write_asset(
        project.metadata.project_id, _raster("image/png"), "image/png"
    )
    assert repository.delete_asset(project.metadata.project_id, reference)
    assert note.read_bytes() == b"keep"
    assert orphan.read_bytes() == b"keep"


@pytest.mark.parametrize("linked_part", ["directory", "file"])
def test_linked_or_reparse_boundaries_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, linked_part: str
) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    reference = repository.write_asset(
        project.metadata.project_id, _raster("image/png"), "image/png"
    )
    suspect = (
        _project_path(tmp_path) / "assets"
        if linked_part == "directory"
        else _project_path(tmp_path) / reference
    )
    original = Path.is_junction

    def fake_junction(path: Path) -> bool:
        return path == suspect or original(path)

    monkeypatch.setattr(Path, "is_junction", fake_junction)
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.read_asset(project.metadata.project_id, reference)
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.delete_asset(project.metadata.project_id, reference)
    assert suspect.exists()


def test_corrupt_digest_and_signature_are_rejected(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    reference = repository.write_asset(
        project.metadata.project_id, _raster("image/png"), "image/png"
    )
    target = _project_path(tmp_path) / reference
    target.write_bytes(_raster("image/png", b"evil"))
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.read_asset(project.metadata.project_id, reference)
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(project.metadata.project_id, _raster("image/png"), "image/png")
    invalid = b"invalid-signature"
    invalid_ref = f"assets/{hashlib.sha256(invalid).hexdigest()}.png"
    (_project_path(tmp_path) / invalid_ref).write_bytes(invalid)
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.read_asset(project.metadata.project_id, invalid_ref)


@pytest.mark.parametrize("size", [0, 16 * 1024 * 1024 + 1])
def test_corrupt_managed_size_is_rejected(tmp_path: Path, size: int) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    data = b"\x89PNG\r\n\x1a\n" + b"x" * max(0, size - 8)
    if size == 0:
        data = b""
    reference = f"assets/{hashlib.sha256(data).hexdigest()}.png"
    (_project_path(tmp_path) / reference).write_bytes(data)
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.read_asset(project.metadata.project_id, reference)


def test_single_asset_16_mib_boundary(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    data = _raster("image/png", b"x" * (16 * 1024 * 1024 - 8))
    reference = repository.write_asset(project.metadata.project_id, data, "image/png")
    assert len(repository.read_asset(project.metadata.project_id, reference)) == 16 * 1024 * 1024
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(project.metadata.project_id, data + b"x", "image/png")


def test_256_asset_limit_allows_idempotence_at_capacity(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    last_data = b""
    last_reference = ""
    for index in range(256):
        last_data = _raster("image/png", index.to_bytes(2))
        last_reference = repository.write_asset(project.metadata.project_id, last_data, "image/png")
    assert (
        repository.write_asset(project.metadata.project_id, last_data, "image/png")
        == last_reference
    )
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(
            project.metadata.project_id, _raster("image/png", b"extra"), "image/png"
        )
    assert len(list((_project_path(tmp_path) / "assets").iterdir())) == 256


def test_128_mib_project_limit_allows_idempotence_at_capacity(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    last_data = b""
    last_reference = ""
    for index in range(8):
        last_data = _raster("image/png", bytes([index]) + b"x" * (16 * 1024 * 1024 - 9))
        last_reference = repository.write_asset(project.metadata.project_id, last_data, "image/png")
    assert (
        repository.write_asset(project.metadata.project_id, last_data, "image/png")
        == last_reference
    )
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.write_asset(
            project.metadata.project_id, _raster("image/png", b"extra"), "image/png"
        )
    assert len(list((_project_path(tmp_path) / "assets").iterdir())) == 8


def test_reference_aware_delete_checks_values_not_keys(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    reference = repository.write_asset(
        project.metadata.project_id, _raster("image/png"), "image/png"
    )
    saved = repository.save(
        ProjectDocument(metadata=project.metadata, state={"nested": [{"image": reference}]})
    )
    with pytest.raises(ValidationError, match=r"^Invalid project asset\.$"):
        repository.delete_asset(project.metadata.project_id, reference)
    assert repository.read_asset(project.metadata.project_id, reference) == _raster("image/png")
    assert repository.load(project.metadata.project_id) == saved

    repository.save(ProjectDocument(metadata=saved.metadata, state={reference: "not a reference"}))
    assert repository.delete_asset(project.metadata.project_id, reference) is True
    assert repository.delete_asset(project.metadata.project_id, reference) is False
    with pytest.raises(FileNotFoundError, match="Project asset not found"):
        repository.read_asset(project.metadata.project_id, reference)


def test_injected_publication_failure_cleans_only_own_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Raster")
    directory = _project_path(tmp_path) / "assets"
    unrelated = directory / ".aurora-asset-prior"
    unrelated.write_bytes(b"keep")
    original_state = (_project_path(tmp_path) / "state.json").read_bytes()

    def fail_link(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        raise OSError("simulated publication failure")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(OSError, match="simulated publication failure"):
        repository.write_asset(project.metadata.project_id, _raster("image/png"), "image/png")
    assert list(directory.iterdir()) == [unrelated]
    assert unrelated.read_bytes() == b"keep"
    assert (_project_path(tmp_path) / "state.json").read_bytes() == original_state
