"""Pure editor snapshot projection into the approved P4 build input."""

from __future__ import annotations

from src.editor.codec import _validated_document  # pyright: ignore[reportPrivateUsage]
from src.editor.models import EditorDocument, EditorStateError
from src.site_export import (
    StaticSiteAsset,
    StaticSiteBrand,
    StaticSiteDocument,
    StaticSitePage,
    StaticSiteSection,
)


def to_static_site_document(
    editor: EditorDocument,
    assets: tuple[StaticSiteAsset, ...] = (),
) -> StaticSiteDocument:
    """Drop editor IDs, preserve presentation order, and retain supplied bytes."""
    snapshot = _validated_document(editor)
    if type(assets) is not tuple or any(type(item) is not StaticSiteAsset for item in assets):
        raise EditorStateError("Invalid editor state.")
    brand = snapshot.brand
    return StaticSiteDocument(
        language=snapshot.language,
        brand=StaticSiteBrand(
            name=brand.name,
            tagline=brand.tagline,
            primary_color=brand.primary_color,
            secondary_color=brand.secondary_color,
            font_family=brand.font_family,
            logo_path=brand.logo_path,
        ),
        pages=tuple(
            StaticSitePage(
                slug=page.slug,
                title=page.title,
                meta_description=page.meta_description,
                heading=page.heading,
                sections=tuple(
                    StaticSiteSection(
                        heading=section.heading,
                        body=section.body,
                        image_path=section.image_path,
                        image_alt=section.image_alt,
                    )
                    for section in page.sections
                ),
            )
            for page in snapshot.pages
        ),
        assets=assets,
    )


__all__ = ["to_static_site_document"]
