"""AURORA P4-001 immutable site projections and private boundary validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, cast

_MAX_PAGES = 100
_MAX_SECTIONS = 100
_MAX_ASSETS = 256
_MAX_ASSET_BYTES = 16 * 1024 * 1024
_MAX_ASSETS_BYTES = 128 * 1024 * 1024
_MAX_TEXT_BYTES = 64 * 1024
_MAX_TOTAL_TEXT_BYTES = 1024 * 1024
_MAX_BUILD_BYTES = 150 * 1024 * 1024
_SLUG = re.compile(r"[a-z][a-z0-9-]{0,63}")
_ASSET = re.compile(r"assets/[a-z0-9_-]+\.(png|jpg|jpeg|gif|webp)")
_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
_DEVICES = frozenset({"con", "prn", "aux", "nul", "conin$", "conout$"}) | frozenset(
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
)


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteBrand:
    """Detached brand presentation, not persisted editor state."""

    name: str
    tagline: str
    primary_color: str = "#4F46E5"
    secondary_color: str = "#0F172A"
    font_family: Literal["system", "serif", "monospace"] = "system"
    logo_path: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteSection:
    """Plain text section with an optional local raster image."""

    heading: str
    body: str
    image_path: str | None = None
    image_alt: str = ""


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSitePage:
    """One root-level semantic page."""

    slug: str
    title: str
    meta_description: str
    heading: str
    sections: tuple[StaticSiteSection, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteAsset:
    """Caller-supplied immutable raster bytes; no filesystem source."""

    path: str
    data: bytes = field(repr=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteDocument:
    """Typed compilation projection supplied by a future application caller."""

    language: Literal["ru", "en"]
    brand: StaticSiteBrand
    pages: tuple[StaticSitePage, ...]
    assets: tuple[StaticSiteAsset, ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteFile:
    """One trusted compiled artifact, with relative path and immutable bytes."""

    path: str
    data: bytes = field(repr=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class StaticSiteBuild:
    """Detached compilation result; exporter does not sanitize its contents."""

    files: tuple[StaticSiteFile, ...]


class SiteValidationError(ValueError):
    """Invalid site projection, compiled artifact or export destination."""


class SiteExportError(RuntimeError):
    """Output I/O failed; the local cause is preserved for diagnostics."""


def _invalid() -> SiteValidationError:
    return SiteValidationError("Invalid static site input.")


def _text(value: object, *, required: bool = False) -> int:
    if type(value) is not str or "\x00" in value or (required and not value.strip()):
        raise _invalid()
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        raise _invalid() from None
    if size > _MAX_TEXT_BYTES:
        raise _invalid()
    return size


def _items(value: object, maximum: int | None = None) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise _invalid()
    result = cast("tuple[object, ...]", value)
    if maximum is not None and len(result) > maximum:
        raise _invalid()
    return result


def _safe_name(value: object, *, asset: bool = False) -> str:
    _text(value, required=True)
    name = cast("str", value)
    pattern = _ASSET if asset else _SLUG
    if pattern.fullmatch(name) is None:
        raise _invalid()
    basename = name.rsplit("/", 1)[-1].split(".", 1)[0]
    if basename in _DEVICES:
        raise _invalid()
    return name


def _bytes(value: object, maximum: int) -> bytes:
    if type(value) is not bytes or not value or len(value) > maximum:
        raise _invalid()
    return value


def _unique(names: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for name in names:
        key = name.casefold()
        if key in seen:
            raise _invalid()
        seen.add(key)
    for key in seen:
        parts = key.split("/")
        if any("/".join(parts[:end]) in seen for end in range(1, len(parts))):
            raise _invalid()


def _signature(path: str, data: bytes) -> None:
    extension = path.rsplit(".", 1)[-1]
    if extension == "png":
        valid = data.startswith(b"\x89PNG\r\n\x1a\n")
    elif extension in ("jpg", "jpeg"):
        valid = data.startswith(b"\xff\xd8\xff")
    elif extension == "gif":
        valid = data.startswith((b"GIF87a", b"GIF89a"))
    else:
        valid = len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if not valid:
        raise _invalid()


# Package-private sharing is explicitly owned by PC-004, not a public API.
def _validate_document(value: object) -> StaticSiteDocument:  # pyright: ignore[reportUnusedFunction]
    if type(value) is not StaticSiteDocument:
        raise _invalid()
    document = value
    if document.language not in ("ru", "en"):
        raise _invalid()
    if type(document.brand) is not StaticSiteBrand:
        raise _invalid()
    brand = document.brand
    total_text = _text(document.language) + _text(brand.name, required=True)
    for text in (brand.tagline, brand.primary_color, brand.secondary_color, brand.font_family):
        total_text += _text(text)
    if (
        _COLOR.fullmatch(brand.primary_color) is None
        or _COLOR.fullmatch(brand.secondary_color) is None
    ):
        raise _invalid()
    if brand.font_family not in ("system", "serif", "monospace"):
        raise _invalid()
    asset_names: list[str] = []
    total_assets = 0
    for item in _items(document.assets, _MAX_ASSETS):
        if type(item) is not StaticSiteAsset:
            raise _invalid()
        name = _safe_name(item.path, asset=True)
        data = _bytes(item.data, _MAX_ASSET_BYTES)
        _signature(name, data)
        total_text += _text(name)
        total_assets += len(data)
        asset_names.append(name)
    _unique(tuple(asset_names))
    if total_assets > _MAX_ASSETS_BYTES:
        raise _invalid()
    if brand.logo_path is not None:
        logo = _safe_name(brand.logo_path, asset=True)
        total_text += _text(logo)
        if logo not in asset_names:
            raise _invalid()
    page_names: list[str] = []
    for item in _items(document.pages, _MAX_PAGES):
        if type(item) is not StaticSitePage:
            raise _invalid()
        page_names.append(_safe_name(item.slug))
        total_text += _text(item.slug) + _text(item.title, required=True)
        total_text += _text(item.meta_description) + _text(item.heading, required=True)
        for section in _items(item.sections, _MAX_SECTIONS):
            if type(section) is not StaticSiteSection:
                raise _invalid()
            total_text += _text(section.heading, required=True) + _text(section.body)
            total_text += _text(section.image_alt, required=section.image_path is not None)
            if section.image_path is not None:
                image = _safe_name(section.image_path, asset=True)
                total_text += _text(image)
                if image not in asset_names:
                    raise _invalid()
    _unique(tuple(page_names))
    if page_names.count("index") != 1 or total_text > _MAX_TOTAL_TEXT_BYTES:
        raise _invalid()
    return document


def _validate_build(value: object) -> tuple[StaticSiteFile, ...]:  # pyright: ignore[reportUnusedFunction]
    if type(value) is not StaticSiteBuild:
        raise _invalid()
    files: list[StaticSiteFile] = []
    size = 0
    for item in _items(value.files):
        if type(item) is not StaticSiteFile:
            raise _invalid()
        _text(item.path, required=True)
        if item.path == "assets/site.css":
            pass
        elif item.path.endswith(".html"):
            _safe_name(item.path[:-5])
        else:
            _safe_name(item.path, asset=True)
        size += len(_bytes(item.data, _MAX_BUILD_BYTES))
        if size > _MAX_BUILD_BYTES:
            raise _invalid()
        files.append(item)
    _unique(tuple(item.path for item in files))
    if sum(item.path == "index.html" for item in files) != 1:
        raise _invalid()
    return tuple(sorted(files, key=lambda item: item.path))


__all__ = [
    "SiteExportError",
    "SiteValidationError",
    "StaticSiteAsset",
    "StaticSiteBrand",
    "StaticSiteBuild",
    "StaticSiteDocument",
    "StaticSiteFile",
    "StaticSitePage",
    "StaticSiteSection",
]
