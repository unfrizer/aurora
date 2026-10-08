"""P7 pure mapping into the approved P4 builder input."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest

from src.editor import (
    EditorBrand,
    EditorDocument,
    EditorPage,
    EditorSection,
    EditorStateError,
    to_static_site_document,
)
from src.site_export import (
    SiteValidationError,
    StaticSiteAsset,
    StaticSiteBuilder,
)

_GIF = bytes.fromhex(
    "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
)


def _document() -> EditorDocument:
    return EditorDocument(
        schema_version=1,
        language="ru",
        brand=EditorBrand(
            name="Студия",
            tagline="Дизайн",
            primary_color="#4F46E5",
            secondary_color="#0F172A",
            font_family="serif",
            logo_path=None,
        ),
        pages=(
            EditorPage(
                id="37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                slug="index",
                title="Главная",
                meta_description="Описание",
                heading="Добро пожаловать",
                sections=(
                    EditorSection(
                        id="8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        heading="Наша команда",
                        body="Текст",
                        image_path=None,
                        image_alt="",
                    ),
                ),
            ),
            EditorPage(
                id="dccd88c9-f674-4d55-b273-a7978cf36c33",
                slug="contact",
                title="Контакты",
                meta_description="Связаться",
                heading="Контакты",
                sections=(),
            ),
        ),
    )


def test_exact_presentation_mapping_drops_ids_and_preserves_order() -> None:
    editor = _document()
    site = to_static_site_document(editor)
    assert site.language == editor.language
    assert site.brand.name == editor.brand.name
    assert site.brand.tagline == editor.brand.tagline
    assert site.brand.primary_color == editor.brand.primary_color
    assert site.brand.secondary_color == editor.brand.secondary_color
    assert site.brand.font_family == editor.brand.font_family
    assert site.brand.logo_path is None
    assert [page.slug for page in site.pages] == ["index", "contact"]
    assert [page.title for page in site.pages] == ["Главная", "Контакты"]
    assert site.pages[0].meta_description == "Описание"
    assert site.pages[0].heading == "Добро пожаловать"
    assert site.pages[0].sections[0].heading == "Наша команда"
    assert site.pages[0].sections[0].body == "Текст"
    assert site.pages[0].sections[0].image_path is None
    assert site.pages[0].sections[0].image_alt == ""
    assert site.assets == ()
    assert not hasattr(site.pages[0], "id")
    assert editor == _document()
    build = StaticSiteBuilder().build(site)
    assert [file.path for file in build.files] == [
        "assets/site.css",
        "contact.html",
        "index.html",
    ]


def test_image_references_are_preserved_with_supplied_immutable_bytes() -> None:
    editor = _document()
    section = replace(
        editor.pages[0].sections[0],
        image_path="assets/logo.gif",
        image_alt="Логотип",
    )
    homepage = replace(editor.pages[0], sections=(section,))
    editor = replace(
        editor,
        brand=replace(editor.brand, logo_path="assets/logo.gif"),
        pages=(homepage, editor.pages[1]),
    )
    assets = (StaticSiteAsset(path="assets/logo.gif", data=_GIF),)
    site = to_static_site_document(editor, assets)
    assert site.assets is assets
    assert site.brand.logo_path == "assets/logo.gif"
    assert site.pages[0].sections[0].image_path == "assets/logo.gif"
    assert site.pages[0].sections[0].image_alt == "Логотип"
    build = StaticSiteBuilder().build(site)
    assert next(file.data for file in build.files if file.path == "assets/logo.gif") == _GIF


@pytest.mark.parametrize("problem", ["slug", "home", "color", "reference", "size"])
def test_p4_builder_remains_authority_for_publishability(problem: str) -> None:
    editor = _document()
    if problem == "slug":
        editor = replace(editor, pages=(replace(editor.pages[0], slug="../escape"),))
    elif problem == "home":
        editor = replace(editor, pages=(editor.pages[1],))
    elif problem == "color":
        editor = replace(editor, brand=replace(editor.brand, primary_color="red"))
    elif problem == "reference":
        editor = replace(editor, brand=replace(editor.brand, logo_path="assets/absent.png"))
    else:
        section = replace(editor.pages[0].sections[0], body="x" * (64 * 1024 + 1))
        editor = replace(editor, pages=(replace(editor.pages[0], sections=(section,)),))
    site = to_static_site_document(editor)
    with pytest.raises(SiteValidationError, match=r"^Invalid static site input\.$"):
        StaticSiteBuilder().build(site)


def test_forged_snapshot_and_mutable_asset_collection_rejected() -> None:
    editor = _document()
    object.__setattr__(editor.pages[0], "sections", ["wrong"])
    with pytest.raises(EditorStateError, match=r"^Invalid editor state\.$"):
        to_static_site_document(editor)
    with pytest.raises(EditorStateError):
        to_static_site_document(
            _document(),
            cast("tuple[StaticSiteAsset, ...]", [StaticSiteAsset(path="assets/a.gif", data=_GIF)]),
        )
    with pytest.raises(EditorStateError):
        to_static_site_document(
            _document(),
            cast("tuple[StaticSiteAsset, ...]", ("not an asset",)),
        )
