"""AURORA P4-001 deterministic, zero-I/O semantic static site compiler."""

from __future__ import annotations

from html import escape

from src.site_export.models import (
    StaticSiteBuild,
    StaticSiteDocument,
    StaticSiteFile,
    _validate_document,  # pyright: ignore[reportPrivateUsage]
)


class StaticSiteBuilder:
    """Compile only typed projections; never reinterpret runtime/project state."""

    __slots__ = ()

    def build(self, document: StaticSiteDocument) -> StaticSiteBuild:
        """Validate completely, then return a sorted immutable self-contained site."""
        document = _validate_document(document)
        brand = document.brand
        fonts = {
            "system": "system-ui, sans-serif",
            "serif": "Georgia, serif",
            "monospace": "ui-monospace, monospace",
        }
        css = (
            ":root { color-scheme: light; "
            f"--primary: {brand.primary_color}; --secondary: {brand.secondary_color}; "
            f"font-family: {fonts[brand.font_family]}; }}\n"
            "* { box-sizing: border-box; }\n"
            "body { margin: 0; color: var(--secondary); background: #fff; }\n"
            "header, main { max-width: 72rem; margin: auto; padding: 2rem; }\n"
            "header { border-bottom: 1px solid #ddd; }\n"
            "nav { display: flex; flex-wrap: wrap; gap: 1rem; }\n"
            "a { color: var(--primary); overflow-wrap: anywhere; }\n"
            "h1, h2, p { overflow-wrap: anywhere; }\n"
            "section { margin: 2rem 0; }\n"
            ".body { white-space: pre-wrap; }\n"
            "img { display: block; max-width: 100%; height: auto; }\n"
            ".logo { max-width: 10rem; }\n"
            "@media (max-width: 600px) { header, main { padding: 1rem; } "
            "nav { flex-direction: column; } }\n"
        )
        files = [StaticSiteFile(path="assets/site.css", data=css.encode("utf-8"))]
        navigation = "\n".join(
            f'<a href="{escape(page.slug)}.html">{escape(page.title)}</a>'
            for page in document.pages
        )
        logo = ""
        if brand.logo_path is not None:
            logo = (
                f'<img class="logo" src="{escape(brand.logo_path)}" alt="{escape(brand.name)}">\n'
            )
        for page in document.pages:
            sections: list[str] = []
            for section in page.sections:
                image = ""
                if section.image_path is not None:
                    image = (
                        f'<img src="{escape(section.image_path)}" '
                        f'alt="{escape(section.image_alt)}">\n'
                    )
                sections.append(
                    f"<section><h2>{escape(section.heading)}</h2>\n"
                    f'<p class="body">{escape(section.body)}</p>\n{image}</section>'
                )
            html = (
                f'<!doctype html>\n<html lang="{document.language}">\n<head>\n'
                '<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                f"<title>{escape(page.title)}</title>\n"
                f'<meta name="description" content="{escape(page.meta_description)}">\n'
                '<link rel="stylesheet" href="assets/site.css">\n</head>\n<body>\n'
                f"<header>{logo}<strong>{escape(brand.name)}</strong>\n"
                f"<p>{escape(brand.tagline)}</p>\n<nav>{navigation}</nav></header>\n"
                f"<main><h1>{escape(page.heading)}</h1>\n"
                + "\n".join(sections)
                + "\n</main>\n</body>\n</html>\n"
            )
            files.append(StaticSiteFile(path=f"{page.slug}.html", data=html.encode("utf-8")))
        files.extend(StaticSiteFile(path=asset.path, data=asset.data) for asset in document.assets)
        return StaticSiteBuild(files=tuple(sorted(files, key=lambda item: item.path)))


__all__ = ["StaticSiteBuilder"]
