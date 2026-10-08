"""P4-001 real compiler/export/reopen integration, without providers or user files."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

from src.site_export import (
    StaticSiteAsset,
    StaticSiteBrand,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSiteExporter,
    StaticSitePage,
    StaticSiteSection,
)


def test_real_static_site_round_trip(tmp_path: Path) -> None:
    # Real one-pixel GIF; signature validation does not promise arbitrary image decoding.
    image = bytes.fromhex(
        "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
    )
    document = StaticSiteDocument(
        language="ru",
        brand=StaticSiteBrand(name="Студия", tagline="Digital studio", logo_path="assets/logo.gif"),
        pages=(
            StaticSitePage(
                slug="index",
                title="Главная",
                meta_description="Студия дизайна",
                heading="Создаём бренды",
                sections=(
                    StaticSiteSection(
                        heading="Наши работы",
                        body="Первый" + "\n" + "Второй",
                        image_path="assets/logo.gif",
                        image_alt="Логотип",
                    ),
                ),
            ),
            StaticSitePage(
                slug="contact",
                title="Контакты",
                meta_description="Связаться",
                heading="Напишите нам",
                sections=(),
            ),
        ),
        assets=(StaticSiteAsset(path="assets/logo.gif", data=image),),
    )
    before = deepcopy(document)
    build = StaticSiteBuilder().build(document)
    exporter = StaticSiteExporter()
    folder = exporter.export_folder(build, tmp_path / "dist")
    archive_path = exporter.export_zip(build, tmp_path / "site.zip")
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for file in build.files:
            assert archive.read(file.path) == (folder / file.path).read_bytes() == file.data
    html = (folder / "index.html").read_text(encoding="utf-8")
    assert "Создаём бренды" in html and 'href="contact.html"' in html
    assert (folder / "assets" / "logo.gif").read_bytes() == image
    assert document == before
    assert not any(path.suffix == ".json" for path in folder.rglob("*"))
