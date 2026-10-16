"""P1-003 public export parent composed with the independent P4 builder/exporter."""

from __future__ import annotations

from pathlib import Path

from src.projects import ProjectRepository
from src.site_export import (
    StaticSiteBrand,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSiteExporter,
    StaticSitePage,
    StaticSiteSection,
)


def test_public_p1_parent_accepts_new_p4_site_without_project_state(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    project = repository.create("Studio", {"private_marker": "not-for-export"})
    project_path = next(tmp_path.iterdir())
    state_before = (project_path / "state.json").read_bytes()
    metadata_before = (project_path / "aurora.project.json").read_bytes()
    document = StaticSiteDocument(
        language="en",
        brand=StaticSiteBrand(name="Studio", tagline="Design"),
        pages=(
            StaticSitePage(
                slug="index",
                title="Home",
                meta_description="Design studio",
                heading="Welcome",
                sections=(StaticSiteSection(heading="Work", body="Our projects"),),
            ),
        ),
    )
    build = StaticSiteBuilder().build(document)

    parent = ProjectRepository(tmp_path).export_directory(project.metadata.project_id)
    destination = parent / "aurora-site-test"
    assert StaticSiteExporter().export_folder(build, destination) == destination
    assert {
        path.relative_to(destination).as_posix(): path.read_bytes()
        for path in destination.rglob("*")
        if path.is_file()
    } == {item.path: item.data for item in build.files}
    assert not any(path.suffix == ".json" for path in destination.rglob("*"))
    assert b"not-for-export" not in b"".join(item.data for item in build.files)
    assert (project_path / "state.json").read_bytes() == state_before
    assert (project_path / "aurora.project.json").read_bytes() == metadata_before
    assert repository.load(project.metadata.project_id) == project
