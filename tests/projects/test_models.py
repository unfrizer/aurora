from dataclasses import FrozenInstanceError

import pytest

from src.projects import ProjectDocument, ProjectMetadata


def test_project_models_are_immutable() -> None:
    metadata = ProjectMetadata(
        project_id="project-1",
        name="Aurora",
        format_version="1.0",
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )
    document = ProjectDocument(metadata=metadata, state={"brand": "Aurora"})

    assert document.metadata.name == "Aurora"
    with pytest.raises(FrozenInstanceError):
        metadata.name = "Other"  # type: ignore[misc]
