"""P6-004 same-origin ZIP download and failure-boundary acceptance."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import cast
from zipfile import ZIP_STORED, ZipFile

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.core.types import JSONDict
from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository
from src.site_export import (
    SiteExportError,
    SiteValidationError,
    StaticSiteBuild,
    StaticSiteBuilder,
    StaticSiteDocument,
    StaticSiteExporter,
)

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-zip"


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
class ZipAPI:
    client: Client
    root: Path
    store: EmptyStore


@pytest.fixture
def api(tmp_path: Path) -> ZipAPI:
    root = tmp_path / "Projects"
    store = EmptyStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    client = cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False))
    return ZipAPI(client, root, store)


def _editor(reference: str | None = None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "language": "ru",
        "brand": {
            "name": "Студия",
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
                "title": "Главная",
                "meta_description": "Заголовок",
                "heading": "Первый заголовок",
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Работы",
                        "body": "Наши проекты",
                        "image_path": reference,
                        "image_alt": "Проект" if reference else "",
                    }
                ],
            }
        ],
    }


def _create(api: ZipAPI) -> tuple[str, str]:
    response = api.client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Студия"})
    assert response.status_code == 201
    metadata = response.json()["metadata"]
    return metadata["project_id"], metadata["updated_at"]


def _save(api: ZipAPI, project_id: str, timestamp: str, editor: dict[str, object]) -> str:
    response = api.client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={"editor": editor, "expected_updated_at": timestamp},
    )
    assert response.status_code == 200
    return response.json()["metadata"]["updated_at"]


def _path(project_id: str) -> str:
    return f"/api/v1/projects/{project_id}/exports/zip"


def test_zip_is_deterministic_p4_artifact_without_project_mutation(
    api: ZipAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    assert uploaded.status_code == 201
    reference = uploaded.json()["path"]
    unused = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=b"\x89PNG\r\n\x1a\nunused-zip",
    )
    assert unused.status_code == 201
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    before = ProjectRepository(api.root).load(project_id)
    reads: list[str] = []
    original_read = ProjectRepository.read_asset

    def observe_read(repository: ProjectRepository, identifier: str, path: str) -> bytes:
        reads.append(path)
        return original_read(repository, identifier, path)

    monkeypatch.setattr(ProjectRepository, "read_asset", observe_read)
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(staging))

    first = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    second = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert reads == [reference, reference]
    assert first.headers["content-type"] == "application/zip"
    assert first.headers["content-disposition"] == 'attachment; filename="aurora-site.zip"'
    assert first.headers["cache-control"] == "no-store"
    assert first.headers["x-content-type-options"] == "nosniff"
    assert first.headers["cross-origin-resource-policy"] == "same-origin"
    assert "access-control-allow-origin" not in first.headers

    with ZipFile(BytesIO(first.content)) as archive:
        names = archive.namelist()
        assert names == sorted(names)
        assert names == sorted(["assets/site.css", reference, "index.html"])
        assert all(item.compress_type == ZIP_STORED for item in archive.infolist())
        assert archive.read(reference) == _IMAGE
        assert "Первый заголовок" in archive.read("index.html").decode("utf-8")
        assert not any(
            name.startswith(("dist/", "site/", "exports/"))
            or name in {"aurora.project.json", "state.json", "settings.json"}
            for name in names
        )
    preview = api.client.get(f"/api/v1/projects/{project_id}/preview/index.html")
    with ZipFile(BytesIO(first.content)) as archive:
        assert preview.content == archive.read("index.html")
    assert ProjectRepository(api.root).load(project_id) == before
    project_directory = next(api.root.iterdir())
    assert list((project_directory / "site").iterdir()) == []
    assert list((project_directory / "exports").iterdir()) == []
    assert list(staging.iterdir()) == []
    assert api.store.calls == 0


def test_request_gate_exact_body_and_missing_project(api: ZipAPI) -> None:
    project_id, timestamp = _create(api)
    path = _path(project_id)
    for body in ({}, {"expected_updated_at": 3}, {"expected_updated_at": timestamp, "x": 1}):
        response = api.client.post(path, headers=_HEADERS, json=body)
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
    for headers in (
        {"Host": "evil", **_HEADERS},
        {"Origin": "https://evil.example", "X-Aurora-Request": "1"},
        {"Origin": _ORIGIN},
    ):
        response = api.client.post(path, headers=headers, json={"expected_updated_at": timestamp})
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
    non_json = api.client.post(
        path, headers={**_HEADERS, "Content-Type": "text/plain"}, content=b"{}"
    )
    assert non_json.status_code == 400
    oversized = api.client.post(
        path, headers=_HEADERS, json={"expected_updated_at": "x" * (2 * 1024 * 1024)}
    )
    assert oversized.status_code == 400
    assert (
        api.client.post(
            _path("bad-id"), headers=_HEADERS, json={"expected_updated_at": timestamp}
        ).status_code
        == 400
    )
    missing = api.client.post(
        _path("00000000-0000-0000-0000-000000000000"),
        headers=_HEADERS,
        json={"expected_updated_at": timestamp},
    )
    assert missing.status_code == 404
    assert missing.json() == {"error": {"code": 404}}
    assert api.store.calls == 0


def test_stale_timestamp_precedes_assets_and_build(
    api: ZipAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    current = _save(api, project_id, timestamp, _editor(f"assets/{'a' * 64}.png"))
    assert current != timestamp

    def forbidden_read(_repository: ProjectRepository, _identifier: str, _path: str) -> bytes:
        raise AssertionError("Asset read after stale timestamp")

    def forbidden_build(
        _builder: StaticSiteBuilder, _document: StaticSiteDocument
    ) -> StaticSiteBuild:
        raise AssertionError("Build after stale timestamp")

    monkeypatch.setattr(ProjectRepository, "read_asset", forbidden_read)
    monkeypatch.setattr(StaticSiteBuilder, "build", forbidden_build)
    stale = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}


@pytest.mark.parametrize("editor", [None, {"schema_version": 2}, {**_editor(), "pages": []}])
def test_missing_unsupported_or_invalid_editor_is_400(api: ZipAPI, editor: object) -> None:
    project_id, _timestamp = _create(api)
    repository = ProjectRepository(api.root)
    current = repository.load(project_id)
    saved = repository.save(
        ProjectDocument(metadata=current.metadata, state=cast("JSONDict", {"editor": editor}))
    )
    response = api.client.post(
        _path(project_id),
        headers=_HEADERS,
        json={"expected_updated_at": saved.metadata.updated_at},
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert repository.load(project_id) == saved


@pytest.mark.parametrize("reference", [f"assets/{'a' * 64}.png", "../secret.png"])
def test_missing_or_malformed_asset_is_400(api: ZipAPI, reference: str) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    response = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "secret" not in response.text


def test_corrupt_asset_and_native_read_are_sanitized(
    api: ZipAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    reference = uploaded.json()["path"]
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    target = next(api.root.iterdir()) / reference
    target.write_bytes(b"\x89PNG\r\n\x1a\ncorrupt")
    corrupt = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert corrupt.status_code == 400
    assert corrupt.json() == {"error": {"code": 400}}

    def fail_read(_repository: ProjectRepository, _identifier: str, _path: str) -> bytes:
        raise OSError("C:\\private\\asset")

    monkeypatch.setattr(ProjectRepository, "read_asset", fail_read)
    failure = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert failure.status_code == 500
    assert failure.json() == {"error": {"code": 500}}
    assert "private" not in failure.text


@pytest.mark.parametrize("failure", [SiteExportError("C:\\secret"), SiteValidationError("secret")])
def test_export_stage_failure_is_fixed_500(
    api: ZipAPI, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())

    def fail_export(_exporter: StaticSiteExporter, _build: object, _path: Path) -> Path:
        raise failure

    monkeypatch.setattr(StaticSiteExporter, "export_zip", fail_export)
    response = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert response.status_code == 500
    assert response.json() == {"error": {"code": 500}}
    assert "secret" not in response.text


def test_staging_read_and_cleanup_failures_are_fixed_500(
    api: ZipAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    original_temporary_directory = tempfile.TemporaryDirectory
    staging_parent = tmp_path / "staging"
    staging_parent.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(staging_parent))

    def fail_staging(*, prefix: str) -> tempfile.TemporaryDirectory[str]:
        raise OSError("C:\\private\\temp")

    monkeypatch.setattr(tempfile, "TemporaryDirectory", fail_staging)
    staging = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert staging.status_code == 500
    assert staging.json() == {"error": {"code": 500}}
    assert "private" not in staging.text
    monkeypatch.setattr(tempfile, "TemporaryDirectory", original_temporary_directory)

    original_read = Path.read_bytes

    def fail_zip_read(path: Path) -> bytes:
        if path.name == "site.zip":
            raise OSError("C:\\private\\zip")
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", fail_zip_read)
    read = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert read.status_code == 500
    assert read.json() == {"error": {"code": 500}}
    assert "private" not in read.text
    assert list(staging_parent.iterdir()) == []
    monkeypatch.setattr(Path, "read_bytes", original_read)

    @contextmanager
    def fail_cleanup(*, prefix: str) -> Generator[str]:
        with original_temporary_directory(prefix=prefix) as directory:
            yield directory
        raise OSError("C:\\private\\cleanup")

    monkeypatch.setattr(tempfile, "TemporaryDirectory", fail_cleanup)
    cleanup = api.client.post(
        _path(project_id), headers=_HEADERS, json={"expected_updated_at": timestamp}
    )
    assert cleanup.status_code == 500
    assert cleanup.json() == {"error": {"code": 500}}
    assert "private" not in cleanup.text
    assert list(staging_parent.iterdir()) == []
