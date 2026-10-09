"""Same-origin, read-only hosting for a built AURORA browser UI."""

from __future__ import annotations

import re
import stat
from pathlib import Path
from typing import cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from src.credentials import WindowsCredentialStore
from src.local_api import create_app

_ASSET_PATH = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_-][A-Za-z0-9_.-]*)*\Z")
_ASSET_MEDIA = {
    ".css": "text/css",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "application/javascript",
    ".png": "image/png",
    ".webp": "image/webp",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}
_STATIC_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


def _is_reparse(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except OSError:
        return False
    attribute = cast(int, getattr(metadata, "st_file_attributes", 0))
    reparse_flag = cast(int, getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    return bool(attribute & reparse_flag) or path.is_symlink() or path.is_junction()


def _safe_ancestors(path: Path) -> bool:
    return not any(_is_reparse(item) for item in (path, *path.parents))


def _regular_file(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except OSError:
        return False
    return stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1 and not _is_reparse(path)


def validate_bundle(ui_root: Path) -> tuple[Path, Path]:
    root = ui_root.absolute()
    assets = root / "assets"
    if not _safe_ancestors(root) or not root.is_dir():
        raise RuntimeError("The built AURORA UI is unavailable.")
    if not _safe_ancestors(assets) or not assets.is_dir():
        raise RuntimeError("The built AURORA UI is unavailable.")
    if not _regular_file(root / "index.html"):
        raise RuntimeError("The built AURORA UI is unavailable.")
    return root, assets


def _static_response(path: Path, *, head: bool, media_type: str) -> Response:
    if not _safe_ancestors(path) or not _regular_file(path):
        raise HTTPException(status_code=404)
    try:
        data = path.read_bytes()
    except OSError:
        raise HTTPException(status_code=404) from None
    headers = {**_STATIC_HEADERS, "Content-Length": str(len(data))}
    return Response(content=b"" if head else data, media_type=media_type, headers=headers)


def create_desktop_app(
    *,
    project_root: Path,
    credential_store: WindowsCredentialStore,
    allowed_origin: str,
    ui_root: Path,
) -> FastAPI:
    """Compose P6 with a minimal, nonlinked static UI boundary."""
    root, assets = validate_bundle(ui_root)
    app = create_app(
        project_root=project_root,
        credential_store=credential_store,
        allowed_origin=allowed_origin,
    )

    def index(request: Request) -> Response:
        return _static_response(
            root / "index.html", head=request.method == "HEAD", media_type="text/html"
        )

    def asset(asset_path: str, request: Request) -> Response:
        raw_path = request.scope.get("raw_path")
        if isinstance(raw_path, bytes) and b"%" in raw_path:
            raise HTTPException(status_code=404)
        if _ASSET_PATH.fullmatch(asset_path) is None:
            raise HTTPException(status_code=404)
        candidate = assets.joinpath(*asset_path.split("/"))
        try:
            inside_assets = candidate.resolve(strict=False).is_relative_to(
                assets.resolve(strict=True)
            )
        except (OSError, RuntimeError):
            raise HTTPException(status_code=404) from None
        if not inside_assets:
            raise HTTPException(status_code=404)
        media_type = _ASSET_MEDIA.get(candidate.suffix.lower())
        if media_type is None:
            raise HTTPException(status_code=404)
        return _static_response(candidate, head=request.method == "HEAD", media_type=media_type)

    app.add_api_route("/", index, methods=["GET", "HEAD"], include_in_schema=False)
    app.add_api_route(
        "/assets/{asset_path:path}", asset, methods=["GET", "HEAD"], include_in_schema=False
    )
    return app
