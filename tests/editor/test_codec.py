"""P7 strict editor JSON codec and detached-state acceptance."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import cast

import pytest

from src.core.types import JSONDict, JSONValue
from src.editor import (
    EditorDocument,
    EditorStateError,
    load_editor_state,
    save_editor_state,
)

_PAGE_ID = "37d407e8-9af8-4ca4-9e57-c0c28cce4266"
_SECTION_ID = "8bc80959-6e1d-4ad1-aa1e-9678e404c980"


def _state() -> JSONDict:
    return {
        "outside": {"panel": ["left", "right"]},
        "editor": {
            "schema_version": 1,
            "language": "ru",
            "brand": {
                "name": "Студия",
                "tagline": "Творим",
                "primary_color": "#4F46E5",
                "secondary_color": "#0F172A",
                "font_family": "system",
                "logo_path": None,
            },
            "pages": [
                {
                    "id": _PAGE_ID,
                    "slug": "index",
                    "title": "Главная",
                    "meta_description": "Описание",
                    "heading": "Привет",
                    "sections": [
                        {
                            "id": _SECTION_ID,
                            "heading": "Наша команда",
                            "body": "Текст",
                            "image_path": None,
                            "image_alt": "",
                        }
                    ],
                }
            ],
        },
    }


def _editor(state: JSONDict) -> dict[str, JSONValue]:
    return cast("dict[str, JSONValue]", state["editor"])


def _pages(state: JSONDict) -> list[JSONValue]:
    return cast("list[JSONValue]", _editor(state)["pages"])


def _page(state: JSONDict) -> dict[str, JSONValue]:
    return cast("dict[str, JSONValue]", _pages(state)[0])


def _sections(state: JSONDict) -> list[JSONValue]:
    return cast("list[JSONValue]", _page(state)["sections"])


def _section(state: JSONDict) -> dict[str, JSONValue]:
    return cast("dict[str, JSONValue]", _sections(state)[0])


def _document() -> EditorDocument:
    document = load_editor_state(_state())
    assert document is not None
    return document


def test_missing_editor_is_only_none_case() -> None:
    assert load_editor_state({}) is None
    with pytest.raises(EditorStateError, match=r"^Invalid editor state\.$"):
        load_editor_state({"editor": None})


def test_round_trip_preserves_exact_shape_order_and_outer_keys() -> None:
    source = _state()
    document = load_editor_state(source)
    assert document is not None
    assert document.pages[0].sections[0].id == _SECTION_ID
    saved = save_editor_state(source, document)
    assert saved == source
    assert saved is not source
    assert saved["editor"] is not source["editor"]
    assert saved["outside"] is not source["outside"]
    assert load_editor_state(saved) == document


def test_loaded_snapshot_is_detached_from_mutated_json_input() -> None:
    source = _state()
    loaded = load_editor_state(source)
    assert loaded is not None
    cast("dict[str, JSONValue]", _editor(source)["brand"])["name"] = "Changed"
    _section(source)["body"] = "Changed"
    assert loaded.brand.name == "Студия"
    assert loaded.pages[0].sections[0].body == "Текст"


def test_language_page_and_section_order_are_stable() -> None:
    source = _state()
    first = _page(source)
    _sections(source).append(
        {
            "id": "0657ab59-4b34-4fbb-9cb3-feb3e30d6b76",
            "heading": "Второй блок",
            "body": "",
            "image_path": None,
            "image_alt": "",
        }
    )
    second = deepcopy(first)
    second["id"] = "dccd88c9-f674-4d55-b273-a7978cf36c33"
    second["slug"] = "contact"
    second["sections"] = []
    _pages(source).append(second)
    _editor(source)["language"] = "en"
    document = load_editor_state(source)
    assert document is not None
    assert document.language == "en"
    assert [page.slug for page in document.pages] == ["index", "contact"]
    assert [section.heading for section in document.pages[0].sections] == [
        "Наша команда",
        "Второй блок",
    ]
    assert save_editor_state({}, document)["editor"] == source["editor"]


@pytest.mark.parametrize("version", [0, 2, True, "1", None])
def test_unsupported_version_rejected(version: JSONValue) -> None:
    source = _state()
    _editor(source)["schema_version"] = version
    with pytest.raises(EditorStateError, match=r"^Invalid editor state\.$"):
        load_editor_state(source)


@pytest.mark.parametrize(
    ("target", "field", "value"),
    [
        ("editor", "language", "de"),
        ("editor", "language", 1),
        ("brand", "font_family", "webfont"),
        ("brand", "name", 3),
        ("brand", "logo_path", 3),
        ("page", "title", None),
        ("section", "image_alt", []),
    ],
)
def test_invalid_field_types_and_vocabularies_rejected(
    target: str, field: str, value: JSONValue
) -> None:
    source = _state()
    locations = {
        "editor": _editor(source),
        "brand": cast("dict[str, JSONValue]", _editor(source)["brand"]),
        "page": _page(source),
        "section": _section(source),
    }
    locations[target][field] = value
    with pytest.raises(EditorStateError, match=r"^Invalid editor state\.$"):
        load_editor_state(source)


@pytest.mark.parametrize("target", ["editor", "brand", "page", "section"])
def test_unknown_or_missing_key_rejected(target: str) -> None:
    source = _state()
    locations = {
        "editor": _editor(source),
        "brand": cast("dict[str, JSONValue]", _editor(source)["brand"]),
        "page": _page(source),
        "section": _section(source),
    }
    locations[target]["unknown"] = "SECRET"
    with pytest.raises(EditorStateError) as error:
        load_editor_state(source)
    assert str(error.value) == "Invalid editor state."
    del locations[target]["unknown"]
    del locations[target][next(iter(locations[target]))]
    with pytest.raises(EditorStateError):
        load_editor_state(source)


@pytest.mark.parametrize("target", ["editor", "brand", "pages", "page", "sections", "section"])
def test_wrong_nested_container_shape_rejected(target: str) -> None:
    source = _state()
    if target == "editor":
        source["editor"] = []
    elif target == "brand":
        _editor(source)["brand"] = []
    elif target == "pages":
        _editor(source)["pages"] = {}
    elif target == "page":
        _pages(source)[0] = []
    elif target == "sections":
        _page(source)["sections"] = {}
    else:
        _sections(source)[0] = []
    with pytest.raises(EditorStateError, match=r"^Invalid editor state\.$"):
        load_editor_state(source)


@pytest.mark.parametrize("identifier", ["", "UPPERCASE", "37D407E8-9AF8-4CA4-9E57-C0C28CCE4266"])
def test_noncanonical_uuid_rejected(identifier: str) -> None:
    source = _state()
    _page(source)["id"] = identifier
    with pytest.raises(EditorStateError):
        load_editor_state(source)


def test_duplicate_page_and_global_section_ids_rejected() -> None:
    source = _state()
    _pages(source).append(deepcopy(_page(source)))
    with pytest.raises(EditorStateError):
        load_editor_state(source)
    _page(source)["id"] = "dccd88c9-f674-4d55-b273-a7978cf36c33"
    with pytest.raises(EditorStateError):
        load_editor_state(source)
    _pages(source).pop()
    _sections(source).append(deepcopy(_section(source)))
    with pytest.raises(EditorStateError):
        load_editor_state(source)


def test_existing_unsupported_editor_cannot_be_clobbered() -> None:
    source = _state()
    _editor(source)["schema_version"] = 2
    before = deepcopy(source)
    with pytest.raises(EditorStateError):
        save_editor_state(source, _document())
    assert source == before


def test_save_deeply_detaches_opaque_outer_state() -> None:
    source = _state()
    saved = save_editor_state(source, _document())
    outside = cast("dict[str, JSONValue]", source["outside"])
    panels = cast("list[JSONValue]", outside["panel"])
    panels.append("secret")
    assert saved["outside"] == {"panel": ["left", "right"]}
    cast("dict[str, JSONValue]", saved["outside"])["new"] = "value"
    assert "new" not in outside


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), object()])
def test_non_json_outer_values_rejected(bad: object) -> None:
    source = _state()
    source["outside"] = cast("JSONValue", bad)
    with pytest.raises(EditorStateError):
        save_editor_state(source, _document())


def test_cyclic_outer_value_is_rejected_without_mutation() -> None:
    source = _state()
    cycle: JSONDict = {}
    cycle["self"] = cycle
    source["outside"] = cycle
    with pytest.raises(EditorStateError):
        save_editor_state(source, _document())
    assert cycle["self"] is cycle


def test_forged_snapshot_is_rejected_without_coercion() -> None:
    document = _document()
    object.__setattr__(document.brand, "name", 3)
    with pytest.raises(EditorStateError):
        save_editor_state({}, document)
    clean = _document()
    object.__setattr__(clean, "pages", [clean.pages[0]])
    with pytest.raises(EditorStateError):
        save_editor_state({}, clean)


def test_save_rejects_bad_outer_keys_and_preserves_existing_input() -> None:
    source = _state()
    source[cast("str", 4)] = "bad key"
    with pytest.raises(EditorStateError):
        save_editor_state(source, _document())
    assert cast("dict[object, object]", source)[4] == "bad key"


def test_new_editor_can_be_saved_into_empty_p1_state() -> None:
    document = _document()
    saved = save_editor_state({}, replace(document, language="en"))
    assert load_editor_state(saved) == replace(document, language="en")
