"""Temporary P1 persistence through P7 state and P4 static build."""

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
from src.site_export import StaticSiteBuilder


def test_real_project_save_reopen_editor_to_text_site(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    repository = ProjectRepository(root)
    created = repository.create("Студия")
    assert created.state == {}
    assert load_editor_state(created.state) is None
    editor = EditorDocument(
        schema_version=1,
        language="ru",
        brand=EditorBrand(
            name="Студия",
            tagline="Сделано для вас",
            primary_color="#4F46E5",
            secondary_color="#0F172A",
            font_family="system",
            logo_path=None,
        ),
        pages=(
            EditorPage(
                id="37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                slug="index",
                title="Студия — главная",
                meta_description="Дизайн-студия",
                heading="Добро пожаловать",
                sections=(
                    EditorSection(
                        id="8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        heading="Услуги",
                        body="Создаём визуальный стиль",
                        image_path=None,
                        image_alt="",
                    ),
                ),
            ),
        ),
    )
    state = save_editor_state({"notes": {"origin": "test"}}, editor)
    saved = repository.save(ProjectDocument(metadata=created.metadata, state=state))
    reopened = ProjectRepository(root).load(saved.metadata.project_id)
    assert reopened.state["notes"] == {"origin": "test"}
    loaded = load_editor_state(reopened.state)
    assert loaded == editor
    assert loaded is not editor
    assert loaded is not None
    site = to_static_site_document(loaded)
    build = StaticSiteBuilder().build(site)
    html = next(file.data for file in build.files if file.path == "index.html")
    assert b'<html lang="ru">' in html
    assert "Дизайн-студия".encode() in html
    assert "Создаём визуальный стиль".encode() in html
    assert [file.path for file in build.files] == ["assets/site.css", "index.html"]
    assert not (root / "dist").exists()
