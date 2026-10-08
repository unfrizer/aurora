"""P6-003 read-only preview acceptance over temporary saved projects."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.core.types import JSONDict
from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository
from src.site_export import StaticSiteBuild, StaticSiteBuilder, StaticSiteDocument

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_CSP = (
    "default-src 'none'; style-src 'self'; img-src 'self'; "
    "script-src 'none'; connect-src 'none'; form-action 'none'; "
    "base-uri 'none'; frame-ancestors 'self'"
)
_RASTERS = {
    "image/png": b"\x89PNG\r\n\x1a\npreview",
    "image/jpeg": b"\xff\xd8\xffpreview",
    "image/gif": b"GIF89apreview",
    "image/webp": b"RIFF\x00\x00\x00\x00WEBPpreview",
}


class EmptyStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        raise AssertionError("Unexpected credential read")

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        raise AssertionError("Unexpected credential delete")


@dataclass(frozen=True)
class PreviewAPI:
    client: Client
    store: EmptyStore
    root: Path


@pytest.fixture
def api(tmp_path: Path) -> Iterator[PreviewAPI]:
    root = tmp_path / "Projects"
    store = EmptyStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield PreviewAPI(client, store, root)


def _create(client: Client) -> tuple[str, str]:
    response = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Studio"})
    assert response.status_code == 201
    metadata = response.json()["metadata"]
    return metadata["project_id"], metadata["updated_at"]


def _editor(language: Literal["ru", "en"], reference: str | None = None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "language": language,
        "brand": {
            "name": "Студия" if language == "ru" else "Studio",
            "tagline": "Идеи",
            "primary_color": "#4F46E5",
            "secondary_color": "#0F172A",
            "font_family": "system",
            "logo_path": reference,
        },
        "pages": [
            {
                "id": "37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                "slug": "index",
                "title": "Главная" if language == "ru" else "Home",
                "meta_description": "Local preview",
                "heading": "Welcome",
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Work",
                        "body": "Safe <script> text",
                        "image_path": reference,
                        "image_alt": "Work image" if reference else "",
                    }
                ],
            },
            {
                "id": "a833f4b1-fafe-4af2-b635-8cd515c2fd40",
                "slug": "about",
                "title": "О нас" if language == "ru" else "About",  # noqa: RUF001
                "meta_description": "Second page",
                "heading": "About us",
                "sections": [],
            },
        ],
    }


def _save(client: Client, project_id: str, timestamp: str, editor: dict[str, object]) -> None:
    response = client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={"editor": editor, "expected_updated_at": timestamp},
    )
    assert response.status_code == 200


def _preview(project_id: str, file_path: str) -> str:
    return f"/api/v1/projects/{project_id}/preview/{file_path}"


@pytest.mark.parametrize("language", ["ru", "en"])
def test_html_css_navigation_security_and_p4_compiler(
    api: PreviewAPI, monkeypatch: pytest.MonkeyPatch, language: Literal["ru", "en"]
) -> None:
    project_id, timestamp = _create(api.client)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_RASTERS["image/png"],
    )
    assert uploaded.status_code == 201
    reference = uploaded.json()["path"]
    unused = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=b"\x89PNG\r\n\x1a\nunused",
    )
    assert unused.status_code == 201
    _save(api.client, project_id, timestamp, _editor(language, reference))
    before = ProjectRepository(api.root).load(project_id)
    built: list[StaticSiteDocument] = []
    reads: list[str] = []
    original_build = StaticSiteBuilder.build
    original_read = ProjectRepository.read_asset

    def observe(builder: StaticSiteBuilder, document: StaticSiteDocument) -> StaticSiteBuild:
        built.append(document)
        return original_build(builder, document)

    def observe_read(repository: ProjectRepository, identifier: str, path: str) -> bytes:
        reads.append(path)
        return original_read(repository, identifier, path)

    monkeypatch.setattr(StaticSiteBuilder, "build", observe)
    monkeypatch.setattr(ProjectRepository, "read_asset", observe_read)
    index = api.client.get(_preview(project_id, "index.html"))
    about = api.client.get(_preview(project_id, "about.html"))
    css = api.client.get(_preview(project_id, "assets/site.css"))
    raster = api.client.get(_preview(project_id, reference))
    assert all(item.status_code == 200 for item in (index, about, css, raster))
    assert built and all(len(item.assets) == 1 for item in built)
    assert all(item.assets[0].path == reference for item in built)
    assert all(item.assets[0].data == _RASTERS["image/png"] for item in built)
    assert reads and set(reads) == {reference}
    assert f'<html lang="{language}">' in index.text
    assert 'href="about.html"' in index.text
    assert "Safe &lt;script&gt; text" in index.text
    assert "About us" in about.text
    assert "max-width: 600px" in css.text
    assert raster.content == _RASTERS["image/png"]
    for response, media in (
        (index, "text/html; charset=utf-8"),
        (about, "text/html; charset=utf-8"),
        (css, "text/css; charset=utf-8"),
        (raster, "image/png"),
    ):
        assert response.headers["content-type"] == media
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["cross-origin-resource-policy"] == "same-origin"
        assert "access-control-allow-origin" not in response.headers
    assert index.headers["content-security-policy"] == _CSP
    assert about.headers["content-security-policy"] == _CSP
    assert "content-security-policy" not in css.headers
    assert ProjectRepository(api.root).load(project_id) == before
    directory = next(api.root.iterdir())
    assert list((directory / "site").iterdir()) == []
    assert list((directory / "exports").iterdir()) == []
    assert api.store.calls == 0


@pytest.mark.parametrize(("media_type", "data"), tuple(_RASTERS.items()))
def test_preview_raster_has_canonical_media_type(
    api: PreviewAPI, media_type: str, data: bytes
) -> None:
    project_id, timestamp = _create(api.client)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": media_type},
        content=data,
    )
    assert uploaded.status_code == 201
    reference = uploaded.json()["path"]
    _save(api.client, project_id, timestamp, _editor("en", reference))
    response = api.client.get(_preview(project_id, reference))
    assert response.status_code == 200
    assert response.headers["content-type"] == media_type
    assert response.content == data


def test_missing_editor_invalid_draft_and_unsupported_state_are_fixed_400(
    api: PreviewAPI,
) -> None:
    project_id, _timestamp = _create(api.client)
    repository = ProjectRepository(api.root)
    path = _preview(project_id, "index.html")
    empty = api.client.get(path)
    assert empty.status_code == 400
    assert empty.json() == {"error": {"code": 400}}
    editor_states: tuple[object, ...] = (
        None,
        {"schema_version": 2},
        {**_editor("en"), "pages": []},
    )
    for editor in editor_states:
        current = repository.load(project_id)
        saved = repository.save(
            ProjectDocument(
                metadata=current.metadata,
                state=cast("JSONDict", {"editor": editor}),
            )
        )
        response = api.client.get(path)
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
        assert repository.load(project_id) == saved


@pytest.mark.parametrize(
    "reference",
    [f"assets/{'a' * 64}.png", "../private.png", "C:\\private\\image.png"],
)
def test_missing_or_malformed_referenced_asset_is_fixed_400(
    api: PreviewAPI, reference: str
) -> None:
    project_id, timestamp = _create(api.client)
    _save(api.client, project_id, timestamp, _editor("en", reference))
    before = ProjectRepository(api.root).load(project_id)
    response = api.client.get(_preview(project_id, "index.html"))
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "private" not in response.text
    assert ProjectRepository(api.root).load(project_id) == before


def test_corrupt_asset_and_native_io_error_are_sanitized(
    api: PreviewAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api.client)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_RASTERS["image/png"],
    )
    reference = uploaded.json()["path"]
    _save(api.client, project_id, timestamp, _editor("en", reference))
    path = _preview(project_id, "index.html")
    target = next(api.root.iterdir()) / reference
    target.write_bytes(b"\x89PNG\r\n\x1a\ncorrupt")
    corrupt = api.client.get(path)
    assert corrupt.status_code == 400
    assert corrupt.json() == {"error": {"code": 400}}
    target.write_bytes(_RASTERS["image/png"])

    def fail_read(_repository: ProjectRepository, _project_id: str, _path: str) -> bytes:
        raise OSError("C:\\private\\asset")

    monkeypatch.setattr(ProjectRepository, "read_asset", fail_read)
    failure = api.client.get(path)
    assert failure.status_code == 500
    assert failure.json() == {"error": {"code": 500}}
    assert "private" not in failure.text


def test_nonmember_paths_missing_project_and_existing_request_gate(
    api: PreviewAPI,
) -> None:
    project_id, timestamp = _create(api.client)
    _save(api.client, project_id, timestamp, _editor("en"))
    for member in ("", "state.json", "assets/../../state.json", "index.html/extra"):
        response = api.client.get(_preview(project_id, member))
        assert response.status_code == 404
        assert response.json() == {"error": {"code": 404}}
    assert api.client.get(_preview("not-a-uuid", "index.html")).status_code == 400
    absent = api.client.get(_preview("00000000-0000-0000-0000-000000000000", "index.html"))
    assert absent.status_code == 404
    assert absent.json() == {"error": {"code": 404}}
    denied = api.client.get(_preview(project_id, "index.html"), headers={"Host": "evil"})
    assert denied.status_code == 400
    foreign = api.client.get(
        _preview(project_id, "index.html"), headers={"Origin": "https://evil.example"}
    )
    assert foreign.status_code == 200
    assert "access-control-allow-origin" not in foreign.headers
    mutation = api.client.post(_preview(project_id, "index.html"), headers=_HEADERS, json={})
    assert mutation.status_code == 405
    assert mutation.json() == {"error": {"code": 405}}
    assert api.store.calls == 0
