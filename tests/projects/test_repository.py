import json
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from src.core.exceptions import ValidationError
from src.core.types import JSONDict, JSONValue
from src.projects import ProjectDocument, ProjectRepository


def test_create_persists_portable_project_structure(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)

    document = repository.create("My Business", {"pages": ["home"]})
    project_path = next(tmp_path.iterdir())

    assert project_path.name.endswith(document.metadata.project_id)
    assert (project_path / "aurora.project.json").is_file()
    assert (project_path / "state.json").is_file()
    assert all((project_path / name).is_dir() for name in ("assets", "site", "exports"))
    assert repository.load(document.metadata.project_id) == document


def test_save_reopens_and_lists_updated_project(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Aurora")
    changed = ProjectDocument(metadata=original.metadata, state={"seo": {"title": "Hello"}})

    saved = repository.save(changed)

    assert saved.metadata.updated_at >= original.metadata.updated_at
    assert repository.load(saved.metadata.project_id) == saved
    assert repository.list() == (saved.metadata,)


def test_invalid_name_and_non_json_state_are_rejected(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)

    with pytest.raises(ValidationError):
        repository.create(" ")
    with pytest.raises(ValidationError):
        repository.create("Aurora", {"invalid": {1, 2}})  # type: ignore[arg-type]


def test_delete_removes_the_project_directory(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    document = repository.create("Aurora")

    repository.delete(document.metadata.project_id)

    with pytest.raises(FileNotFoundError):
        repository.load(document.metadata.project_id)


def test_list_uses_complete_uuid_and_rename_survives_reopen(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original")
    renamed = ProjectDocument(
        metadata=replace(original.metadata, name="Renamed"), state={"name": "new"}
    )
    saved = repository.save(renamed)

    assert ProjectRepository(tmp_path).list() == (saved.metadata,)
    assert repository.load(original.metadata.project_id) == saved


@pytest.mark.parametrize("project_id", ["*", "../*", "", "not-a-uuid"])
def test_invalid_identity_cannot_match_or_delete_projects(tmp_path: Path, project_id: str) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Safe")

    with pytest.raises(ValidationError, match="UUID"):
        repository.delete(project_id)
    with pytest.raises(ValidationError, match="UUID"):
        repository.load(project_id)

    assert repository.load(original.metadata.project_id) == original


@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_state_is_rejected_without_creating_files(tmp_path: Path, number: float) -> None:
    with pytest.raises(ValidationError):
        ProjectRepository(tmp_path).create("Invalid", {"nested": [number]})
    assert not list(tmp_path.iterdir())


def test_circular_and_non_string_key_state_are_rejected(tmp_path: Path) -> None:
    state: JSONDict = {}
    state["cycle"] = state
    repository = ProjectRepository(tmp_path)

    with pytest.raises(ValidationError, match="circular"):
        repository.create("Invalid", state)
    with pytest.raises(ValidationError, match="keys"):
        repository.create("Invalid", cast(JSONDict, {1: "value"}))
    assert not list(tmp_path.iterdir())


def test_state_is_detached_at_persistence_boundaries(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    nested: list[JSONValue] = ["original"]
    document = repository.create("Detached", {"pages": nested})
    nested.append("caller mutation")
    assert document.state == {"pages": ["original"]}

    document.state["pages"] = ["changed"]
    assert repository.load(document.metadata.project_id).state == {"pages": ["original"]}
    saved = repository.save(document)
    document.state["pages"] = ["another mutation"]
    assert saved.state == {"pages": ["changed"]}
    assert repository.load(document.metadata.project_id) == saved


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("format_version", "2.0"),
        ("name", 1),
        ("project_id", "bad"),
        ("created_at", "2026-10-05T00:00:00"),
        ("updated_at", "not-a-date"),
        ("unexpected", "field"),
    ],
)
def test_corrupt_metadata_is_rejected(tmp_path: Path, field: str, value: object) -> None:
    repository = ProjectRepository(tmp_path)
    document = repository.create("Original")
    file = next(tmp_path.iterdir()) / "aurora.project.json"
    metadata = cast(dict[str, object], json.loads(file.read_text(encoding="utf-8")))
    metadata[field] = value
    file.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValidationError):
        repository.load(document.metadata.project_id)
    with pytest.raises(ValidationError):
        repository.list()


def test_save_rejects_changed_creation_time_and_preserves_disk(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original", {"value": "old"})
    changed = ProjectDocument(
        metadata=replace(original.metadata, created_at="2000-01-01T00:00:00+00:00"),
        state={"value": "new"},
    )
    with pytest.raises(ValidationError, match="creation time"):
        repository.save(changed)
    assert repository.load(original.metadata.project_id) == original


def test_failed_metadata_replacement_rolls_back_state_and_removes_temporary_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original", {"value": "old"})
    replace_file = Path.replace

    def fail_metadata(path: Path, target: str | Path) -> Path:
        if Path(target).name == "aurora.project.json":
            raise OSError("simulated replacement failure")
        return replace_file(path, target)

    monkeypatch.setattr(Path, "replace", fail_metadata)
    with pytest.raises(OSError):
        repository.save(ProjectDocument(metadata=original.metadata, state={"value": "new"}))

    assert repository.load(original.metadata.project_id) == original
    assert not list(tmp_path.rglob(".aurora-*"))


def test_failed_create_removes_only_its_new_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Preserved")

    def fail_replace(path: Path, target: str | Path) -> Path:
        raise OSError("simulated write failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError):
        repository.create("Failed")
    assert repository.list() == (original.metadata,)


def test_duplicate_project_directories_are_not_silently_selected(tmp_path: Path) -> None:
    import shutil

    repository = ProjectRepository(tmp_path)
    original = repository.create("Original")
    project_path = next(tmp_path.iterdir())
    shutil.copytree(project_path, tmp_path / f"copy-{original.metadata.project_id}")

    with pytest.raises(ValidationError, match="Multiple"):
        repository.load(original.metadata.project_id)
    with pytest.raises(ValidationError, match="Multiple"):
        repository.list()


def test_project_directory_identity_must_match_its_metadata(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    repository.create("Original")
    project_path = next(tmp_path.iterdir())
    project_path.rename(tmp_path / "mismatched-directory")
    with pytest.raises(ValidationError, match="identity"):
        repository.list()


def test_linked_project_directory_is_rejected_before_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original")
    project_path = next(tmp_path.iterdir())
    original_is_junction = Path.is_junction

    def is_junction(path: Path) -> bool:
        return path == project_path or original_is_junction(path)

    monkeypatch.setattr(Path, "is_junction", is_junction)
    with pytest.raises(ValidationError, match="direct directory"):
        repository.delete(original.metadata.project_id)
    assert (project_path / "state.json").exists()


def test_linked_state_file_is_rejected_before_save(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original", {"value": "old"})
    state_path = next(tmp_path.iterdir()) / "state.json"
    original_is_symlink = Path.is_symlink

    def is_symlink(path: Path) -> bool:
        return path == state_path or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", is_symlink)
    with pytest.raises(ValidationError, match="link outside"):
        repository.save(ProjectDocument(metadata=original.metadata, state={"value": "new"}))
    assert json.loads(state_path.read_text(encoding="utf-8")) == {"value": "old"}


def test_listing_orders_utc_timestamps_chronologically_not_lexically(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    older = repository.create("Older")
    newer = repository.create("Newer")
    for path in tmp_path.iterdir():
        file = path / "aurora.project.json"
        metadata = cast(dict[str, object], json.loads(file.read_text(encoding="utf-8")))
        metadata["updated_at"] = (
            "9998-01-01T00:00:00Z"
            if metadata["project_id"] == older.metadata.project_id
            else "9998-01-01T00:00:00.100000+00:00"
        )
        file.write_text(json.dumps(metadata), encoding="utf-8")
    assert tuple(item.project_id for item in repository.list()) == (
        newer.metadata.project_id,
        older.metadata.project_id,
    )


def test_backwards_clock_cannot_persist_invalid_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ProjectRepository(tmp_path)
    original = repository.create("Original")
    monkeypatch.setattr(ProjectRepository, "_now", staticmethod(lambda: "2000-01-01T00:00:00Z"))
    with pytest.raises(ValidationError, match="timestamps"):
        repository.save(ProjectDocument(metadata=original.metadata, state={"changed": True}))
    assert repository.load(original.metadata.project_id) == original
