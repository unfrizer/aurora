"""P4 builder/exporter to P5 fake-Netlify integration, without live requests."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

import pytest

import src.deployment.netlify as netlify
from src.deployment import NetlifyDeployer
from src.site_export import (
    StaticSiteBrand,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSitePage,
    StaticSiteSection,
)

_SITE_ID = "00000000-0000-0000-0000-000000000001"


class _Reply:
    status = 200

    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self, size: int) -> bytes:
        return self._data[:size]


def test_compiled_ru_site_reaches_exact_zip_and_ready_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = StaticSiteDocument(
        language="ru",
        brand=StaticSiteBrand(name="Аврора", tagline="Простой сайт"),
        pages=(
            StaticSitePage(
                slug="index",
                title="Главная",
                meta_description="Описание",
                heading="Добро пожаловать",
                sections=(StaticSiteSection(heading="Услуги", body="Текст"),),
            ),
        ),
    )
    build = StaticSiteBuilder().build(document)
    original_files = build.files
    requests: list[tuple[str, str, bytes | None, dict[str, str]]] = []
    replies = [
        _Reply(b'{"id":"00000000-0000-0000-0000-000000000001"}'),
        _Reply(b'{"id":"deploy-1"}'),
        _Reply(b'{"id":"deploy-1","state":"ready","ssl_url":"https://aurora.netlify.app"}'),
    ]

    class FakeConnection:
        def __init__(self, host: str, *, timeout: int) -> None:
            assert host == "api.netlify.com"
            assert timeout == 30

        def request(
            self,
            method: str,
            path: str,
            body: bytes | None = None,
            headers: dict[str, str] | None = None,
        ) -> None:
            requests.append((method, path, body, headers or {}))

        def getresponse(self) -> _Reply:
            return replies.pop(0)

        def close(self) -> None:
            return None

    monkeypatch.setattr(netlify, "HTTPSConnection", FakeConnection)
    result = NetlifyDeployer("synthetic-token").deploy(build)

    assert result.site_id == _SITE_ID
    assert result.deploy_id == "deploy-1"
    assert result.public_url == "https://aurora.netlify.app"
    assert build.files == original_files
    assert len(requests) == 3
    archive_bytes = requests[1][2]
    assert archive_bytes is not None
    with ZipFile(BytesIO(archive_bytes)) as archive:
        assert archive.namelist() == [file.path for file in build.files]
        for file in build.files:
            assert archive.read(file.path) == file.data
        assert b'lang="ru"' in archive.read("index.html")
    assert requests[1][3]["Authorization"] == "Bearer synthetic-token"
    assert all("synthetic-token" not in file.path for file in build.files)
