"""P1 saved raster reference through P7 projection into P4 build."""

from __future__ import annotations

from pathlib import Path

from src.editor import (
    EditorBrand,
    EditorDocument,
    EditorPage,
    EditorSection,
    load_editor_state,
    save_editor_state,
    to_static_site_document,
)
from src.projects import ProjectDocument, ProjectRepository
from src.site_export import StaticSiteAsset, StaticSiteBuilder


def test_saved_image_survives_reopen_and_builds_static_site(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path)
    created = repository.create("Studio", {"notes": "preserved"})
    image = b"\x89PNG\r\n\x1a\nsynthetic-raster"
    reference = repository.write_asset(created.metadata.project_id, image, "image/png")
    editor = EditorDocument(
        schema_version=1,
        language="en",
        brand=EditorBrand(
            name="Studio",
            tagline="Visual ideas",
            primary_color="#4F46E5",
            secondary_color="#0F172A",
            font_family="system",
            logo_path=reference,
        ),
        pages=(
            EditorPage(
                id="37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                slug="index",
                title="Studio — Home",
                meta_description="Design studio",
                heading="Welcome",
                sections=(
                    EditorSection(
                        id="8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        heading="Work",
                        body="Made for you",
                        image_path=reference,
                        image_alt="Studio work",
                    ),
                ),
            ),
        ),
    )
    saved_state = save_editor_state(created.state, editor)
    repository.save(ProjectDocument(metadata=created.metadata, state=saved_state))

    reopened = ProjectRepository(tmp_path)
    document = reopened.load(created.metadata.project_id)
    assert document.state["notes"] == "preserved"
    loaded = load_editor_state(document.state)
    assert loaded == editor
    assert loaded is not None
    detached_image = reopened.read_asset(created.metadata.project_id, reference)
    site = to_static_site_document(
        loaded, assets=(StaticSiteAsset(path=reference, data=detached_image),)
    )
    built = StaticSiteBuilder().build(site)
    outputs = {item.path: item.data for item in built.files}
    assert outputs[reference] == image
    assert reference.encode() in outputs["index.html"]
    assert b"Design studio" in outputs["index.html"]
    assert not (tmp_path / "dist").exists()
