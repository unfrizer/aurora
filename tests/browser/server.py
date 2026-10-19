"""Isolated composed app for the Windows browser acceptance gate."""

from __future__ import annotations

import json
import os
import re
import struct
import zlib
from pathlib import Path
from unittest.mock import patch

import uvicorn

from src.credentials import SecretName, WindowsCredentialStore
from src.deployment import NetlifyDeployer, NetlifyDeployment
from src.generation import (
    GenerationJob,
    GenerationRequest,
    GenerationResult,
    ImageGenerationJob,
    ImageGenerationRequest,
    ImageGenerationResult,
    OpenAIImageClient,
    OpenAIResponsesClient,
)
from src.launcher import create_desktop_app
from src.preferences import PreferencesStore
from src.site_export import StaticSiteBuild

_ROOT_NAME = re.compile(r"browser-e2e-[0-9a-f-]{36}\Z")

def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))


_IMAGE = (
    b"\x89PNG\r\n\x1a\n"
    + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    + _png_chunk(b"IDAT", zlib.compress(b"\x00\x5b\x4e\xe9\xff"))
    + _png_chunk(b"IEND", b"")
)


class _FakeCredentials(WindowsCredentialStore):
    def __init__(self) -> None:
        self._values: dict[SecretName, str] = {}

    def set_secret(self, name: SecretName, secret: str) -> None:
        self._values[name] = secret

    def get_secret(self, name: SecretName) -> str | None:
        return self._values.get(name)

    def delete_secret(self, name: SecretName) -> bool:
        return self._values.pop(name, None) is not None


def _fake_text(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
    output = {
        "brand": {
            "name": "Северная студия",
            "tagline": "Дизайн для бизнеса",
            "primary_color": "#123456",
            "secondary_color": "#abcdef",
            "font_family": "system",
        },
        "pages": [{
            "slug": "index",
            "title": "Северная студия",
            "meta_description": "Дизайн и брендинг",
            "heading": "Добро пожаловать",
            "sections": [{"heading": "Услуги", "body": "Дизайн для вашего проекта"}],
        }],
    }
    return GenerationJob(
        "a0000000-0000-4000-8000-000000000001",
        request,
        "completed",
        result=GenerationResult("browser-fake-response", request.model, json.dumps(output)),
    )


def _fake_image(_client: OpenAIImageClient, request: ImageGenerationRequest) -> ImageGenerationJob:
    return ImageGenerationJob(
        "a0000000-0000-4000-8000-000000000003",
        request,
        "completed",
        result=ImageGenerationResult(_IMAGE),
    )


def _forbid_deploy(
    _deployer: NetlifyDeployer, _build: StaticSiteBuild, *, site_id: str | None = None
) -> NetlifyDeployment:
    raise AssertionError("The offline browser gate must never deploy to Netlify.")


def _isolated_root() -> Path:
    repository = Path(__file__).resolve().parents[2]
    build = repository / "build"
    build.mkdir(exist_ok=True)
    raw = os.environ.get("AURORA_E2E_ROOT", "")
    candidate = Path(raw)
    if (
        not candidate.is_absolute()
        or _ROOT_NAME.fullmatch(candidate.name) is None
        or candidate.parent.resolve() != build.resolve()
        or candidate.exists()
    ):
        raise RuntimeError("The browser test needs a fresh isolated build/ root.")
    candidate.mkdir()
    return candidate


def main() -> None:
    repository = Path(__file__).resolve().parents[2]
    root = _isolated_root()
    port = int(os.environ.get("AURORA_E2E_PORT", "18765"))
    if not 1024 <= port <= 65535:
        raise RuntimeError("Invalid browser test port.")
    origin = f"http://127.0.0.1:{port}"
    app = create_desktop_app(
        project_root=root / "Projects",
        credential_store=_FakeCredentials(),
        allowed_origin=origin,
        ui_root=repository / "frontend" / "dist",
        preferences_store=PreferencesStore(root / "settings.json"),
    )
    with (
        patch.object(OpenAIResponsesClient, "generate", _fake_text),
        patch.object(OpenAIImageClient, "generate", _fake_image),
        patch.object(NetlifyDeployer, "deploy", _forbid_deploy),
    ):
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            access_log=False,
            proxy_headers=False,
            server_header=False,
            log_level="warning",
        )


if __name__ == "__main__":
    main()
