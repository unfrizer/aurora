"""P4-001 exact immutable schemas, API signatures and dependency ownership."""

from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from typing import cast, get_type_hints

import pytest

import src.site_export as gateway
from src.site_export import (
    SiteExportError,
    SiteValidationError,
    StaticSiteAsset,
    StaticSiteBrand,
    StaticSiteBuild,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSiteExporter,
    StaticSiteFile,
    StaticSitePage,
    StaticSiteSection,
)

_SCHEMAS = (
    (
        StaticSiteBrand,
        ("name", "tagline", "primary_color", "secondary_color", "font_family", "logo_path"),
    ),
    (StaticSiteSection, ("heading", "body", "image_path", "image_alt")),
    (StaticSitePage, ("slug", "title", "meta_description", "heading", "sections")),
    (StaticSiteAsset, ("path", "data")),
    (StaticSiteDocument, ("language", "brand", "pages", "assets")),
    (StaticSiteFile, ("path", "data")),
    (StaticSiteBuild, ("files",)),
)


@pytest.mark.parametrize(("model", "names"), _SCHEMAS)
def test_exact_model_schema(
    model: type[
        StaticSiteBrand
        | StaticSiteSection
        | StaticSitePage
        | StaticSiteAsset
        | StaticSiteDocument
        | StaticSiteFile
        | StaticSiteBuild
    ],
    names: tuple[str, ...],
) -> None:
    assert tuple(item.name for item in fields(model)) == names
    assert all(item.kw_only for item in fields(model))
    assert set(cast("tuple[str, ...]", vars(model)["__slots__"])) == set(names)
    hints = get_type_hints(model)
    assert set(hints) == set(names)
    assert not any("Any" in str(hint) or "Unknown" in str(hint) for hint in hints.values())
    assert all(
        item.kind == inspect.Parameter.KEYWORD_ONLY
        for item in inspect.signature(model).parameters.values()
    )


def test_defaults_immutable_bytes_and_no_constructor_validation() -> None:
    brand = StaticSiteBrand(name="Brand", tagline="")
    assert (brand.primary_color, brand.secondary_color, brand.font_family, brand.logo_path) == (
        "#4F46E5",
        "#0F172A",
        "system",
        None,
    )
    section = StaticSiteSection(heading="", body="")
    assert (section.image_path, section.image_alt) == (None, "")
    page = StaticSitePage(
        slug="index", title="Home", meta_description="", heading="H", sections=(section,)
    )
    document = StaticSiteDocument(language="en", brand=brand, pages=(page,))
    assert document.assets == ()
    for item in (
        brand,
        section,
        page,
        document,
        StaticSiteAsset(path="x", data=b"secret"),
        StaticSiteFile(path="x", data=b"secret"),
        StaticSiteBuild(files=()),
    ):
        assert not hasattr(item, "__dict__")
        with pytest.raises(FrozenInstanceError):
            setattr(item, fields(item)[0].name, None)
    assert "secret" not in repr(StaticSiteAsset(path="x", data=b"secret"))
    assert "secret" not in repr(StaticSiteFile(path="x", data=b"secret"))
    assert StaticSiteBuild(files=()) == StaticSiteBuild(files=())
    with pytest.raises(TypeError):
        StaticSiteBrand("Name", "Tagline")  # pyright: ignore[reportCallIssue]


def test_exact_api_and_no_service_state() -> None:
    assert gateway.__all__ == sorted(
        {
            "SiteExportError",
            "SiteValidationError",
            "StaticSiteAsset",
            "StaticSiteBrand",
            "StaticSiteBuild",
            "StaticSiteBuilder",
            "StaticSiteDocument",
            "StaticSiteExporter",
            "StaticSiteFile",
            "StaticSitePage",
            "StaticSiteSection",
        }
    )
    assert SiteValidationError.__bases__ == (ValueError,)
    assert SiteExportError.__bases__ == (RuntimeError,)
    assert str(inspect.signature(StaticSiteBuilder)) == "()"
    assert str(inspect.signature(StaticSiteExporter)) == "()"
    assert get_type_hints(StaticSiteBuilder.build) == {
        "document": StaticSiteDocument,
        "return": StaticSiteBuild,
    }
    for method in (StaticSiteExporter.export_folder, StaticSiteExporter.export_zip):
        assert get_type_hints(method) == {
            "build": StaticSiteBuild,
            "destination": Path,
            "return": Path,
        }
    assert [name for name in vars(StaticSiteBuilder) if not name.startswith("_")] == ["build"]
    assert [name for name in vars(StaticSiteExporter) if not name.startswith("_")] == [
        "export_folder",
        "export_zip",
    ]
    assert not hasattr(StaticSiteBuilder(), "__dict__")
    assert not hasattr(StaticSiteExporter(), "__dict__")


def test_import_dag_and_no_higher_or_lower_owner_changes() -> None:
    root = Path(__file__).parents[2]
    package = root / "src" / "site_export"
    assert {path.name for path in package.glob("*.py")} == {
        "__init__.py",
        "models.py",
        "builder.py",
        "exporter.py",
    }
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.level == 0
                module = node.module or ""
                if module.startswith("src."):
                    allowed = {"src.site_export.models"}
                    if path.name == "__init__.py":
                        allowed |= {"src.site_export.builder", "src.site_export.exporter"}
                    assert module in allowed
                    assert path.name != "models.py"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "print"
    for path in (root / "src").rglob("*.py"):
        if package not in path.parents:
            assert "src.site_export" not in path.read_text(encoding="utf-8")
