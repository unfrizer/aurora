"""P7 model, gateway and import-boundary acceptance."""

from __future__ import annotations

import ast
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass
from inspect import signature
from pathlib import Path
from typing import Literal, get_type_hints

import pytest

import src.editor as gateway
from src.editor import EditorBrand, EditorDocument, EditorPage, EditorSection, EditorStateError


def test_gateway_has_exact_approved_symbols() -> None:
    assert set(gateway.__all__) == {
        "EditorBrand",
        "EditorDocument",
        "EditorPage",
        "EditorSection",
        "EditorStateError",
        "load_editor_state",
        "save_editor_state",
        "to_static_site_document",
    }
    assert {name for name in gateway.__all__ if getattr(gateway, name) is None} == set()
    assert issubclass(EditorStateError, ValueError)
    assert str(EditorStateError("Invalid editor state.")) == "Invalid editor state."


def test_public_function_signatures_are_exact() -> None:
    assert str(signature(gateway.load_editor_state)) == (
        "(state: 'JSONDict') -> 'EditorDocument | None'"
    )
    assert str(signature(gateway.save_editor_state)) == (
        "(state: 'JSONDict', editor: 'EditorDocument') -> 'JSONDict'"
    )
    assert str(signature(gateway.to_static_site_document)) == (
        "(editor: 'EditorDocument', assets: 'tuple[StaticSiteAsset, ...]' = ())"
        " -> 'StaticSiteDocument'"
    )


def test_models_are_exact_frozen_slotted_keyword_only_dataclasses() -> None:
    expected = {
        EditorBrand: {
            "name": str,
            "tagline": str,
            "primary_color": str,
            "secondary_color": str,
            "font_family": Literal["system", "serif", "monospace"],
            "logo_path": str | None,
        },
        EditorSection: {
            "id": str,
            "heading": str,
            "body": str,
            "image_path": str | None,
            "image_alt": str,
        },
        EditorPage: {
            "id": str,
            "slug": str,
            "title": str,
            "meta_description": str,
            "heading": str,
            "sections": tuple[EditorSection, ...],
        },
        EditorDocument: {
            "schema_version": Literal[1],
            "language": Literal["ru", "en"],
            "brand": EditorBrand,
            "pages": tuple[EditorPage, ...],
        },
    }
    for model, model_fields in expected.items():
        assert is_dataclass(model)
        assert get_type_hints(model) == model_fields
        assert [item.name for item in fields(model)] == list(model_fields)
        assert all(item.kw_only and item.default is MISSING for item in fields(model))
        assert not hasattr(model, "__dict__") or "__slots__" in vars(model)

    brand = EditorBrand(
        name="A",
        tagline="",
        primary_color="#000000",
        secondary_color="#ffffff",
        font_family="system",
        logo_path=None,
    )
    assert not hasattr(brand, "__dict__")
    with pytest.raises(FrozenInstanceError):
        brand.name = "B"  # type: ignore[misc]
    with pytest.raises(TypeError):
        EditorBrand("A", "", "#000000", "#ffffff", "system", None)  # type: ignore[misc]


def test_production_imports_stay_inside_approved_application_boundary() -> None:
    root = Path(__file__).parents[2]
    package = root / "src" / "editor"
    assert {path.name for path in package.glob("*.py")} == {
        "__init__.py",
        "models.py",
        "codec.py",
        "projection.py",
    }
    allowed: dict[str, set[str]] = {
        "__init__.py": {"src.editor.codec", "src.editor.models", "src.editor.projection"},
        "models.py": set(),
        "codec.py": {"src.core.types", "src.editor.models"},
        "projection.py": {"src.editor.codec", "src.editor.models", "src.site_export"},
    }
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.level == 0
                module = node.module or ""
                if module.startswith("src."):
                    assert module in allowed[path.name]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "print"
    approved_consumer = root / "src" / "local_api" / "app.py"
    for path in (root / "src").rglob("*.py"):
        if package in path.parents:
            continue
        source = path.read_text(encoding="utf-8")
        if path == approved_consumer:
            assert source.count("src.editor") == 1
            tree = ast.parse(source)
            imports = [
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and node.module is not None
                and node.module.startswith("src.editor")
            ]
            assert imports == ["src.editor"]
            assert not any(
                isinstance(node, ast.Import)
                and any(alias.name.startswith("src.editor") for alias in node.names)
                for node in ast.walk(tree)
            )
        else:
            assert "src.editor" not in source
