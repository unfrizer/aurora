"""Strict, detached JSON codec for the approved editor subtree."""

from __future__ import annotations

import json
import math
from typing import cast
from uuid import UUID

from src.core.types import JSONDict, JSONValue
from src.editor.models import (
    EditorBrand,
    EditorDocument,
    EditorPage,
    EditorSection,
    EditorStateError,
)

_EDITOR_KEYS = frozenset({"schema_version", "language", "brand", "pages"})
_BRAND_KEYS = frozenset(
    {"name", "tagline", "primary_color", "secondary_color", "font_family", "logo_path"}
)
_PAGE_KEYS = frozenset({"id", "slug", "title", "meta_description", "heading", "sections"})
_SECTION_KEYS = frozenset({"id", "heading", "body", "image_path", "image_alt"})


def _invalid() -> EditorStateError:
    return EditorStateError("Invalid editor state.")


def _object(value: object, keys: frozenset[str]) -> dict[str, object]:
    if type(value) is not dict:
        raise _invalid()
    result = cast("dict[object, object]", value)
    if len(result) != len(keys) or any(type(key) is not str or key not in keys for key in result):
        raise _invalid()
    return cast("dict[str, object]", result)


def _list(value: object) -> list[object]:
    if type(value) is not list:
        raise _invalid()
    return cast("list[object]", value)


def _text(value: object) -> str:
    if type(value) is not str:
        raise _invalid()
    result = value
    try:
        result.encode("utf-8")
    except UnicodeError:
        raise _invalid() from None
    return result


def _nullable_text(value: object) -> str | None:
    return None if value is None else _text(value)


def _uuid(value: object) -> str:
    identifier = _text(value)
    try:
        if str(UUID(identifier)) != identifier:
            raise _invalid()
    except ValueError:
        raise _invalid() from None
    return identifier


def _brand(value: object) -> EditorBrand:
    source = _object(value, _BRAND_KEYS)
    font = _text(source["font_family"])
    if font not in ("system", "serif", "monospace"):
        raise _invalid()
    return EditorBrand(
        name=_text(source["name"]),
        tagline=_text(source["tagline"]),
        primary_color=_text(source["primary_color"]),
        secondary_color=_text(source["secondary_color"]),
        font_family=font,
        logo_path=_nullable_text(source["logo_path"]),
    )


def _section(value: object) -> EditorSection:
    source = _object(value, _SECTION_KEYS)
    return EditorSection(
        id=_uuid(source["id"]),
        heading=_text(source["heading"]),
        body=_text(source["body"]),
        image_path=_nullable_text(source["image_path"]),
        image_alt=_text(source["image_alt"]),
    )


def _page(value: object, section_ids: set[str]) -> EditorPage:
    source = _object(value, _PAGE_KEYS)
    sections: list[EditorSection] = []
    for item in _list(source["sections"]):
        section = _section(item)
        if section.id in section_ids:
            raise _invalid()
        section_ids.add(section.id)
        sections.append(section)
    return EditorPage(
        id=_uuid(source["id"]),
        slug=_text(source["slug"]),
        title=_text(source["title"]),
        meta_description=_text(source["meta_description"]),
        heading=_text(source["heading"]),
        sections=tuple(sections),
    )


def _decode_payload(value: object) -> EditorDocument:
    source = _object(value, _EDITOR_KEYS)
    if type(source["schema_version"]) is not int or source["schema_version"] != 1:
        raise _invalid()
    language = _text(source["language"])
    if language not in ("ru", "en"):
        raise _invalid()
    pages: list[EditorPage] = []
    page_ids: set[str] = set()
    section_ids: set[str] = set()
    for item in _list(source["pages"]):
        page = _page(item, section_ids)
        if page.id in page_ids:
            raise _invalid()
        page_ids.add(page.id)
        pages.append(page)
    return EditorDocument(
        schema_version=1,
        language=language,
        brand=_brand(source["brand"]),
        pages=tuple(pages),
    )


def _encode_payload(value: object) -> JSONDict:
    if type(value) is not EditorDocument:
        raise _invalid()
    editor = value
    if type(editor.brand) is not EditorBrand or type(editor.pages) is not tuple:
        raise _invalid()
    brand = editor.brand
    pages: list[JSONValue] = []
    for item in editor.pages:
        if type(item) is not EditorPage or type(item.sections) is not tuple:
            raise _invalid()
        sections: list[JSONValue] = []
        for section in item.sections:
            if type(section) is not EditorSection:
                raise _invalid()
            sections.append(
                {
                    "id": section.id,
                    "heading": section.heading,
                    "body": section.body,
                    "image_path": section.image_path,
                    "image_alt": section.image_alt,
                }
            )
        pages.append(
            {
                "id": item.id,
                "slug": item.slug,
                "title": item.title,
                "meta_description": item.meta_description,
                "heading": item.heading,
                "sections": sections,
            }
        )
    payload: JSONDict = {
        "schema_version": editor.schema_version,
        "language": editor.language,
        "brand": {
            "name": brand.name,
            "tagline": brand.tagline,
            "primary_color": brand.primary_color,
            "secondary_color": brand.secondary_color,
            "font_family": brand.font_family,
            "logo_path": brand.logo_path,
        },
        "pages": pages,
    }
    _decode_payload(payload)
    return payload


def _validated_document(value: object) -> EditorDocument:  # pyright: ignore[reportUnusedFunction]
    return _decode_payload(_encode_payload(value))


def _clone_json(value: object, ancestors: set[int]) -> JSONValue:
    if value is None:
        return None
    if type(value) is str:
        return _text(value)
    if type(value) is bool or type(value) is int:
        return value
    if type(value) is float:
        number = value
        if math.isfinite(number):
            return number
        raise _invalid()
    if type(value) is not dict and type(value) is not list:
        raise _invalid()
    container = cast("dict[object, object] | list[object]", value)
    identity = id(container)
    if identity in ancestors:
        raise _invalid()
    ancestors.add(identity)
    try:
        if type(container) is list:
            return [_clone_json(item, ancestors) for item in container]
        result: JSONDict = {}
        for key, item in cast("dict[object, object]", container).items():
            if type(key) is not str:
                raise _invalid()
            result[key] = _clone_json(item, ancestors)
        return result
    finally:
        ancestors.remove(identity)


def load_editor_state(state: JSONDict) -> EditorDocument | None:
    """Decode only the versioned editor subtree, leaving other state opaque."""
    if type(state) is not dict:
        raise _invalid()
    if "editor" not in state:
        return None
    return _decode_payload(state["editor"])


def save_editor_state(state: JSONDict, editor: EditorDocument) -> JSONDict:
    """Replace an approved editor subtree in a detached JSON-compatible state."""
    if type(state) is not dict:
        raise _invalid()
    if "editor" in state:
        _decode_payload(state["editor"])
    payload = _encode_payload(editor)
    try:
        copied = _clone_json(state, set())
        json.dumps(copied, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (RecursionError, UnicodeError, OverflowError, TypeError, ValueError):
        raise _invalid() from None
    if type(copied) is not dict:
        raise _invalid()
    result = cast("JSONDict", copied)
    result["editor"] = payload
    return result


__all__ = ["load_editor_state", "save_editor_state"]
