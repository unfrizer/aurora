"""P6-008 confirmed, project-local folder export and failure boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from httpx import Client, Response

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
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-folder"
_ROUTE = "/api/v1/projects/{project_id}/exports/folder"


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
class FolderAPI:
    client: Client
    root: Path
    store: EmptyStore


@pytest.fixture
def api(tmp_path: Path) -> FolderAPI:
    root = tmp_path / "Projects"
    store = EmptyStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    client = cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False))
    return FolderAPI(client, root, store)


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
                "meta_description": "Студия и проекты",
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


def _create(api: FolderAPI) -> tuple[str, str]:
    response = api.client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Студия"})
    assert response.status_code == 201
    metadata = response.json()["metadata"]
    return metadata["project_id"], metadata["updated_at"]


def _save(api: FolderAPI, project_id: str, timestamp: str, editor: dict[str, object]) -> str:
    response = api.client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={"editor": editor, "expected_updated_at": timestamp},
    )
    assert response.status_code == 200
    return response.json()["metadata"]["updated_at"]


def _post(api: FolderAPI, project_id: str, timestamp: str) -> Response:
    return api.client.post(
        _ROUTE.format(project_id=project_id),
        headers=_HEADERS,
        json={"expected_updated_at": timestamp, "confirm_export": True},
    )


def _error(response: Response, status: int) -> None:
    assert response.status_code == status
    assert response.json() == {"error": {"code": status}}
    assert "folder_path" not in response.text
    assert "C:\\private" not in response.text


def test_new_unique_folders_match_saved_site_without_mutation(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    upload = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    assert upload.status_code == 201
    reference = upload.json()["path"]
    unused = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=b"\x89PNG\r\n\x1a\nunrelated-folder",
    )
    assert unused.status_code == 201
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    repository = ProjectRepository(api.root)
    before = repository.load(project_id)
    parent = repository.export_directory(project_id)
    prior = parent / "prior-export"
    prior.mkdir()
    (prior / "keep.txt").write_text("old", encoding="utf-8")
    project_directory = parent.parent
    site_before = tuple((project_directory / "site").iterdir())
    asset_before = {
        path.name: path.read_bytes() for path in (project_directory / "assets").iterdir()
    }
    reads: list[str] = []
    original_read = ProjectRepository.read_asset

    def observe_read(repo: ProjectRepository, identifier: str, path: str) -> bytes:
        reads.append(path)
        return original_read(repo, identifier, path)

    monkeypatch.setattr(ProjectRepository, "read_asset", observe_read)
    first = _post(api, project_id, timestamp)
    second = _post(api, project_id, timestamp)
    assert first.status_code == second.status_code == 201
    assert reads == [reference, reference]
    for response in (first, second):
        assert set(response.json()) == {"folder_path"}
        assert response.headers["content-type"] == "application/json"
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["cross-origin-resource-policy"] == "same-origin"
        assert response.headers["referrer-policy"] == "no-referrer"
        assert "access-control-allow-origin" not in response.headers
        assert "location" not in response.headers
    first_path = Path(first.json()["folder_path"])
    second_path = Path(second.json()["folder_path"])
    assert first_path != second_path
    for path in (first_path, second_path):
        assert path.is_absolute() and path.parent == parent
        assert path.name == f"aurora-site-{UUID(path.name.removeprefix('aurora-site-'))}"
        assert path.name == path.name.lower()
        files = {
            item.relative_to(path).as_posix(): item.read_bytes()
            for item in path.rglob("*")
            if item.is_file()
        }
        assert set(files) == {"index.html", "assets/site.css", reference}
        assert files[reference] == _IMAGE
        assert "Первый заголовок" in files["index.html"].decode("utf-8")
        assert not any(
            name.endswith(("state.json", "aurora.project.json", "settings.json")) for name in files
        )
        assert unused.json()["path"] not in files
    assert {
        item.relative_to(first_path): item.read_bytes()
        for item in first_path.rglob("*")
        if item.is_file()
    } == {
        item.relative_to(second_path): item.read_bytes()
        for item in second_path.rglob("*")
        if item.is_file()
    }
    preview = api.client.get(f"/api/v1/projects/{project_id}/preview/index.html")
    assert preview.content == (first_path / "index.html").read_bytes()
    assert repository.load(project_id) == before
    assert tuple((project_directory / "site").iterdir()) == site_before
    assert {
        path.name: path.read_bytes() for path in (project_directory / "assets").iterdir()
    } == asset_before
    assert (prior / "keep.txt").read_text(encoding="utf-8") == "old"
    assert api.store.calls == 0


def test_strict_body_gate_and_missing_project_create_nothing(api: FolderAPI) -> None:
    project_id, timestamp = _create(api)
    path = _ROUTE.format(project_id=project_id)
    for body in (
        {},
        {"confirm_export": True},
        {"expected_updated_at": timestamp},
        {"expected_updated_at": 3, "confirm_export": True},
        {"expected_updated_at": timestamp, "confirm_export": False},
        {"expected_updated_at": timestamp, "confirm_export": 1},
        {"expected_updated_at": timestamp, "confirm_export": "true"},
        {"expected_updated_at": timestamp, "confirm_export": True, "destination": "C:\\private"},
    ):
        _error(api.client.post(path, headers=_HEADERS, json=body), 400)
    for headers in (
        {"Host": "evil", **_HEADERS},
        {"Origin": "https://evil.example", "X-Aurora-Request": "1"},
        {"Origin": _ORIGIN},
    ):
        _error(
            api.client.post(
                path,
                headers=headers,
                json={"expected_updated_at": timestamp, "confirm_export": True},
            ),
            400,
        )
    _error(
        api.client.post(path, headers={**_HEADERS, "Content-Type": "text/plain"}, content=b"{}"),
        400,
    )
    _error(
        api.client.post(
            path,
            headers=_HEADERS,
            json={"expected_updated_at": "x" * (2 * 1024 * 1024), "confirm_export": True},
        ),
        400,
    )
    _error(_post(api, "bad-id", timestamp), 400)
    _error(_post(api, "00000000-0000-0000-0000-000000000000", timestamp), 404)
    assert list(ProjectRepository(api.root).export_directory(project_id).iterdir()) == []
    assert api.store.calls == 0


def test_stale_timestamp_precedes_asset_build_and_export_parent(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    latest = _save(api, project_id, timestamp, _editor(f"assets/{'a' * 64}.png"))
    assert latest != timestamp

    def forbidden_read(_repo: ProjectRepository, _identifier: str, _path: str) -> bytes:
        raise AssertionError("asset read after stale timestamp")

    def forbidden_build(
        _builder: StaticSiteBuilder, _document: StaticSiteDocument
    ) -> StaticSiteBuild:
        raise AssertionError("build after stale timestamp")

    def forbidden_parent(_repo: ProjectRepository, _identifier: str) -> Path:
        raise AssertionError("parent lookup after stale timestamp")

    monkeypatch.setattr(ProjectRepository, "read_asset", forbidden_read)
    monkeypatch.setattr(StaticSiteBuilder, "build", forbidden_build)
    monkeypatch.setattr(ProjectRepository, "export_directory", forbidden_parent)
    _error(_post(api, project_id, timestamp), 409)


@pytest.mark.parametrize("editor", [None, {"schema_version": 2}, {**_editor(), "pages": []}])
def test_invalid_saved_editor_is_400(api: FolderAPI, editor: object) -> None:
    project_id, _timestamp = _create(api)
    repo = ProjectRepository(api.root)
    current = repo.load(project_id)
    saved = repo.save(
        ProjectDocument(metadata=current.metadata, state=cast("JSONDict", {"editor": editor}))
    )
    _error(_post(api, project_id, saved.metadata.updated_at), 400)
    assert list(repo.export_directory(project_id).iterdir()) == []
    assert repo.load(project_id) == saved


@pytest.mark.parametrize("reference", [f"assets/{'a' * 64}.png", "../secret.png"])
def test_missing_or_malformed_reference_is_400(api: FolderAPI, reference: str) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    _error(_post(api, project_id, timestamp), 400)
    assert list(ProjectRepository(api.root).export_directory(project_id).iterdir()) == []


def test_corrupt_asset_and_invalid_site_are_400(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    upload = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    reference = upload.json()["path"]
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    asset = next(api.root.iterdir()) / reference
    asset.write_bytes(b"\x89PNG\r\n\x1a\ncorrupt")
    _error(_post(api, project_id, timestamp), 400)
    asset.write_bytes(_IMAGE)

    def fail_build(_builder: StaticSiteBuilder, _document: StaticSiteDocument) -> StaticSiteBuild:
        raise SiteValidationError("C:\\private\\site")

    monkeypatch.setattr(StaticSiteBuilder, "build", fail_build)
    _error(_post(api, project_id, timestamp), 400)
    assert list(ProjectRepository(api.root).export_directory(project_id).iterdir()) == []


@pytest.mark.parametrize("invalid_parent", ["missing", "file"])
def test_invalid_export_parent_is_500(api: FolderAPI, invalid_parent: str) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    repository = ProjectRepository(api.root)
    before = repository.load(project_id)
    parent = repository.export_directory(project_id)
    parent.rmdir()
    if invalid_parent == "file":
        parent.write_text("unsafe", encoding="utf-8")
    _error(_post(api, project_id, timestamp), 500)
    assert repository.load(project_id) == before
    assert api.store.calls == 0


def test_native_asset_read_and_export_failures_are_sanitized(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    upload = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    timestamp = _save(api, project_id, timestamp, _editor(upload.json()["path"]))
    parent = ProjectRepository(api.root).export_directory(project_id)

    def fail_read(_repo: ProjectRepository, _identifier: str, _path: str) -> bytes:
        raise OSError("C:\\private\\asset")

    with monkeypatch.context() as patch:
        patch.setattr(ProjectRepository, "read_asset", fail_read)
        _error(_post(api, project_id, timestamp), 500)

    def fail_export(_exporter: StaticSiteExporter, _build: StaticSiteBuild, _path: Path) -> Path:
        raise OSError("C:\\private\\output")

    with monkeypatch.context() as patch:
        patch.setattr(StaticSiteExporter, "export_folder", fail_export)
        _error(_post(api, project_id, timestamp), 500)
    assert list(parent.iterdir()) == []


@pytest.mark.parametrize(
    "failure", [SiteExportError("C:\\private"), SiteValidationError("C:\\private")]
)
def test_p4_export_error_preserves_old_and_partial_children(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    repo = ProjectRepository(api.root)
    before = repo.load(project_id)
    parent = repo.export_directory(project_id)
    prior = parent / "old"
    prior.mkdir()
    (prior / "keep").write_bytes(b"old")

    def fail_export(
        _exporter: StaticSiteExporter, _build: StaticSiteBuild, destination: Path
    ) -> Path:
        destination.mkdir()
        (destination / "partial").write_bytes(b"partial")
        raise failure

    monkeypatch.setattr(StaticSiteExporter, "export_folder", fail_export)
    _error(_post(api, project_id, timestamp), 500)
    assert (prior / "keep").read_bytes() == b"old"
    assert len([path for path in parent.iterdir() if path.name.startswith("aurora-site-")]) == 1
    assert (
        next(path for path in parent.iterdir() if path.name.startswith("aurora-site-"))
        .joinpath("partial")
        .read_bytes()
        == b"partial"
    )
    assert repo.load(project_id) == before


def test_collision_does_not_overwrite_or_retry(
    api: FolderAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    parent = ProjectRepository(api.root).export_directory(project_id)
    fixed_id = UUID("00000000-0000-4000-8000-000000000001")
    occupied = parent / f"aurora-site-{fixed_id}"
    occupied.mkdir()
    (occupied / "keep").write_bytes(b"old")
    monkeypatch.setattr("src.local_api.app.uuid4", lambda: fixed_id)
    _error(_post(api, project_id, timestamp), 500)
    assert list(parent.iterdir()) == [occupied]
    assert (occupied / "keep").read_bytes() == b"old"
    assert api.store.calls == 0
