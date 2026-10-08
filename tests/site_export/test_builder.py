"""P4-001 compiler acceptance, hostile input and exact resource boundaries."""

from __future__ import annotations

from dataclasses import replace
from html import escape
from pathlib import Path
from typing import Literal, cast

import pytest

from src.site_export import (
    SiteValidationError,
    StaticSiteAsset,
    StaticSiteBrand,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSitePage,
    StaticSiteSection,
)

_PNG = b"\x89PNG\r\n\x1a\n"


def _document() -> StaticSiteDocument:
    return StaticSiteDocument(
        language="ru",
        brand=StaticSiteBrand(name="Мой бренд", tagline="Привет"),
        pages=(
            StaticSitePage(
                slug="index",
                title="Главная",
                meta_description="Описание",
                heading="Заголовок",
                sections=(StaticSiteSection(heading="Секция", body="Строка" + "\n" + "Строка"),),
            ),
        ),
    )


@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("font", ["system", "serif", "monospace"])
def test_full_compilation(
    language: Literal["ru", "en"], font: Literal["system", "serif", "monospace"]
) -> None:
    original = _document()
    document = replace(
        original,
        language=language,
        brand=replace(original.brand, font_family=font, logo_path="assets/logo.png"),
        pages=(
            *original.pages,
            replace(
                original.pages[0],
                slug="about",
                title="About",
                sections=(
                    StaticSiteSection(
                        heading="First", body="", image_path="assets/logo.png", image_alt="Photo"
                    ),
                    StaticSiteSection(heading="Second", body="Two"),
                ),
            ),
        ),
        assets=(StaticSiteAsset(path="assets/logo.png", data=_PNG),),
    )
    builder = StaticSiteBuilder()
    build = builder.build(document)
    assert build == builder.build(document) == StaticSiteBuilder().build(document)
    assert tuple(item.path for item in build.files) == (
        "about.html",
        "assets/logo.png",
        "assets/site.css",
        "index.html",
    )
    files = {item.path: item.data for item in build.files}
    html = files["about.html"].decode()
    assert html.startswith(f'<!doctype html>\n<html lang="{language}">')
    assert '<meta charset="utf-8">' in html
    assert 'name="viewport"' in html and "<title>About</title>" in html
    assert 'name="description" content="Описание"' in html
    assert html.count("<h1>") == 1
    assert html.index("First") < html.index("Second")
    assert html.index('href="index.html"') < html.index('href="about.html"')
    assert 'src="assets/logo.png" alt="Мой бренд"' in html
    assert 'src="assets/logo.png" alt="Photo"' in html
    css = files["assets/site.css"].decode()
    assert "@media" in css and "white-space: pre-wrap" in css
    assert "#4F46E5" in css and "#0F172A" in css
    assert {"system": "system-ui", "serif": "Georgia", "monospace": "ui-monospace"}[font] in css
    assert files["assets/logo.png"] == _PNG
    assert original == _document()


def test_plain_text_escaping_no_io_or_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("Compiler attempted I/O")

    document = _document()
    attack = '<script src="https://evil.invalid">&\'"</script>'
    document = replace(
        document,
        brand=replace(document.brand, name=attack, tagline=attack),
        pages=(
            replace(
                document.pages[0],
                title=attack,
                heading=attack,
                meta_description=attack,
                sections=(
                    StaticSiteSection(
                        heading=attack, body=attack, image_path="assets/p.png", image_alt=attack
                    ),
                ),
            ),
        ),
        assets=(StaticSiteAsset(path="assets/p.png", data=_PNG),),
    )
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr("socket.socket", forbidden)
    build = StaticSiteBuilder().build(document)
    html = next(item.data.decode() for item in build.files if item.path == "index.html")
    assert attack not in html and escape(attack) in html
    assert "<script" not in html and 'src="https:' not in html
    assert 'content="' + escape(attack) + '"' in html
    assert not any(item.path.endswith((".js", ".json")) for item in build.files)


@pytest.mark.parametrize(
    "slug",
    [
        "",
        "Index",
        "../index",
        "a/b",
        "a\\b",
        "a.html",
        "https://evil",
        "C:evil",
        "\\\\server",
        "a.",
        "a ",
        "a" * 65,
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "lpt9",
        " a",
        "a\n",
        "a//b",
    ],
)
def test_invalid_slug(slug: str) -> None:
    document = _document()
    with pytest.raises(SiteValidationError, match=r"^Invalid static site input\.$"):
        StaticSiteBuilder().build(replace(document, pages=(replace(document.pages[0], slug=slug),)))


@pytest.mark.parametrize(
    "path",
    [
        "",
        "assets/../p.png",
        "assets/p.svg",
        "/assets/p.png",
        "assets/P.png",
        "assets/site.css",
        "assets/p.png/evil",
        "assets//p.png",
        "assets/p.png ",
        "assets\\p.png",
        "C:/assets/p.png",
        "assets/con.png",
        "assets/com9.jpg",
        "a.png",
    ],
)
def test_invalid_asset_name(path: str) -> None:
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(_document(), assets=(StaticSiteAsset(path=path, data=_PNG),))
        )


@pytest.mark.parametrize(
    ("path", "data"),
    [
        ("assets/a.png", _PNG),
        ("assets/a.jpg", b"\xff\xd8\xff"),
        ("assets/a.jpeg", b"\xff\xd8\xff"),
        ("assets/a.gif", b"GIF87a"),
        ("assets/a.gif", b"GIF89a"),
        ("assets/a.webp", b"RIFFxxxxWEBP"),
    ],
)
def test_raster_signature_policy(path: str, data: bytes) -> None:
    document = replace(_document(), assets=(StaticSiteAsset(path=path, data=data),))
    assert any(item.data == data for item in StaticSiteBuilder().build(document).files)
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(document, assets=(StaticSiteAsset(path=path, data=b"not-image"),))
        )


@pytest.mark.parametrize(
    "target",
    [
        "document",
        "brand",
        "pages",
        "page",
        "sections",
        "section",
        "assets",
        "asset",
        "data",
        "language",
        "name",
        "tagline",
        "color",
        "font",
    ],
)
def test_wrong_runtime_types(target: str) -> None:
    document = _document()
    if target == "document":
        bad = cast("StaticSiteDocument", None)
    elif target == "brand":
        bad = replace(document, brand=cast("StaticSiteBrand", {}))
    elif target == "pages":
        bad = replace(document, pages=cast("tuple[StaticSitePage, ...]", []))
    elif target == "page":
        bad = replace(document, pages=(cast("StaticSitePage", None),))
    elif target == "sections":
        bad = replace(
            document,
            pages=(replace(document.pages[0], sections=cast("tuple[StaticSiteSection, ...]", [])),),
        )
    elif target == "section":
        bad = replace(
            document, pages=(replace(document.pages[0], sections=(cast("StaticSiteSection", {}),)),)
        )
    elif target == "assets":
        bad = replace(document, assets=cast("tuple[StaticSiteAsset, ...]", []))
    elif target == "asset":
        bad = replace(document, assets=(cast("StaticSiteAsset", {}),))
    elif target == "data":
        bad = replace(
            document,
            assets=(StaticSiteAsset(path="assets/a.png", data=cast("bytes", bytearray(_PNG))),),
        )
    elif target == "language":
        bad = replace(document, language=cast("Literal['ru', 'en']", []))
    else:
        values: dict[str, object] = {
            "name": None,
            "tagline": 2,
            "primary_color": {},
            "font_family": [],
        }
        field_name = {"color": "primary_color", "font": "font_family"}.get(target, target)
        brand = replace(document.brand)
        object.__setattr__(brand, field_name, values[field_name])
        bad = replace(document, brand=brand)
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(bad)


@pytest.mark.parametrize(
    "text", ["\x00", "\ud800", "x" * (64 * 1024 + 1)], ids=["nul", "surrogate", "over-limit"]
)
def test_invalid_unicode_nul_text_size(text: str) -> None:
    document = _document()
    with pytest.raises(SiteValidationError) as error:
        StaticSiteBuilder().build(replace(document, brand=replace(document.brand, tagline=text)))
    assert str(error.value) == "Invalid static site input."


@pytest.mark.parametrize("target", ["name", "page_title", "page_heading", "section_heading"])
def test_required_nonempty_text(target: str) -> None:
    document = _document()
    if target == "name":
        document = replace(document, brand=replace(document.brand, name="  "))
    elif target == "section_heading":
        document = replace(
            document,
            pages=(
                replace(document.pages[0], sections=(StaticSiteSection(heading="\n", body=""),)),
            ),
        )
    else:
        page = replace(document.pages[0])
        object.__setattr__(page, target.removeprefix("page_"), "")
        document = replace(document, pages=(page,))
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(document)


@pytest.mark.parametrize(
    "issue",
    [
        "language",
        "primary",
        "secondary",
        "font",
        "empty_pages",
        "missing_home",
        "duplicate_page",
        "duplicate_asset",
        "missing_logo",
        "missing_image",
        "empty_alt",
        "bad_logo",
        "bad_image",
    ],
)
def test_semantic_rejections(issue: str) -> None:
    document = _document()
    page = document.pages[0]
    if issue == "language":
        document = replace(document, language=cast("Literal['ru', 'en']", "de"))
    elif issue in ("primary", "secondary"):
        brand = replace(document.brand)
        object.__setattr__(brand, f"{issue}_color", "red; background:url(https://evil)")
        document = replace(document, brand=brand)
    elif issue == "font":
        document = replace(
            document,
            brand=replace(
                document.brand,
                font_family=cast("Literal['system', 'serif', 'monospace']", "remote"),
            ),
        )
    elif issue == "empty_pages":
        document = replace(document, pages=())
    elif issue == "missing_home":
        document = replace(document, pages=(replace(page, slug="about"),))
    elif issue == "duplicate_page":
        document = replace(document, pages=(page, page))
    elif issue == "duplicate_asset":
        asset = StaticSiteAsset(path="assets/a.png", data=_PNG)
        document = replace(document, assets=(asset, asset))
    elif issue in ("missing_logo", "bad_logo"):
        document = replace(
            document,
            brand=replace(
                document.brand,
                logo_path="assets/a.png" if issue == "missing_logo" else "https://evil",
            ),
        )
    else:
        section = StaticSiteSection(
            heading="H",
            body="",
            image_path=("https://evil" if issue == "bad_image" else "assets/a.png"),
            image_alt="" if issue == "empty_alt" else "alt",
        )
        document = replace(document, pages=(replace(page, sections=(section,)),))
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(document)


def test_pages_sections_assets_and_text_count_limits() -> None:
    document = _document()
    page = document.pages[0]
    pages = (page, *(replace(page, slug=f"p{number}") for number in range(99)))
    assert len(StaticSiteBuilder().build(replace(document, pages=pages)).files) == 101
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(replace(document, pages=(*pages, replace(page, slug="extra"))))
    sections = (StaticSiteSection(heading="H", body=""),) * 100
    StaticSiteBuilder().build(replace(document, pages=(replace(page, sections=sections),)))
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(document, pages=(replace(page, sections=(*sections, sections[0])),))
        )
    assets = tuple(
        StaticSiteAsset(path=f"assets/p{number}.png", data=_PNG) for number in range(256)
    )
    StaticSiteBuilder().build(replace(document, assets=assets))
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(document, assets=(*assets, StaticSiteAsset(path="assets/extra.png", data=_PNG)))
        )
    # UTF-8 byte limit, not codepoint count; exact per-field boundary accepted.
    StaticSiteBuilder().build(
        replace(document, brand=replace(document.brand, tagline="я" * (32 * 1024)))
    )
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(document, brand=replace(document.brand, tagline="я" * (32 * 1024 + 1)))
        )
    many = (StaticSiteSection(heading="H", body="x" * (64 * 1024)),) * 16
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(replace(document, pages=(replace(page, sections=many),)))
    StaticSiteBuilder().build(replace(document, pages=(replace(page, sections=many[:15]),)))


def test_exact_asset_byte_limits() -> None:
    data = _PNG + b"x" * (16 * 1024 * 1024 - len(_PNG))
    assets = tuple(StaticSiteAsset(path=f"assets/p{number}.png", data=data) for number in range(8))
    document = replace(_document(), assets=assets)
    assert len(StaticSiteBuilder().build(document).files) == 10
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(
            replace(document, assets=(*assets, StaticSiteAsset(path="assets/extra.png", data=_PNG)))
        )
    with pytest.raises(SiteValidationError):
        StaticSiteBuilder().build(replace(document, assets=(replace(assets[0], data=data + b"x"),)))
