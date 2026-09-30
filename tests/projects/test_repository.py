from pathlib import Path

import pytest

from src.core.exceptions import ValidationError
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
