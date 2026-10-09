"""P1 → P7 → P4 → P6 ZIP export through public HTTP and app reopen."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import cast
from zipfile import ZipFile

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.editor import load_editor_state, to_static_site_document
from src.local_api import create_app
from src.projects import ProjectRepository
from src.site_export import StaticSiteAsset, StaticSiteBuilder, StaticSiteExporter

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-integration-zip"


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


def _editor(reference: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "language": "en",
        "brand": {
            "name": "Studio",
            "tagline": "Ideas",
            "primary_color": "#4F46E5",
            "secondary_color": "#0F172A",
            "font_family": "system",
            "logo_path": reference,
        },
        "pages": [
            {
                "id": "37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                "slug": "index",
                "title": "Home",
                "meta_description": "Studio site",
                "heading": "First version",
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Work",
                        "body": "Our work",
                        "image_path": reference,
                        "image_alt": "Project",
                    }
                ],
            }
        ],
    }


def test_create_upload_save_zip_reopen_and_match_p4_exporter(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = EmptyStore()
    first = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(first, base_url=_ORIGIN)) as client:
        created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Studio"})
        assert created.status_code == 201
        project_id = created.json()["metadata"]["project_id"]
        uploaded = client.post(
            f"/api/v1/projects/{project_id}/assets",
            headers={**_HEADERS, "Content-Type": "image/png"},
            content=_IMAGE,
        )
        assert uploaded.status_code == 201
        reference = uploaded.json()["path"]
        saved = client.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={
                "editor": _editor(reference),
                "expected_updated_at": created.json()["metadata"]["updated_at"],
            },
        )
        assert saved.status_code == 200
        timestamp = saved.json()["metadata"]["updated_at"]
        route = f"/api/v1/projects/{project_id}/exports/zip"
        first_zip = client.post(route, headers=_HEADERS, json={"expected_updated_at": timestamp})
        assert first_zip.status_code == 200
        preview = client.get(f"/api/v1/projects/{project_id}/preview/index.html")
        assert preview.status_code == 200
        with ZipFile(BytesIO(first_zip.content)) as archive:
            assert archive.read("index.html") == preview.content
            assert archive.read(reference) == _IMAGE
        before = ProjectRepository(root).load(project_id)

    second = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        reopened = client.get(f"/api/v1/projects/{project_id}")
        assert reopened.status_code == 200
        assert reopened.json()["state"]["editor"] == _editor(reference)
        second_zip = client.post(
            route,
            headers=_HEADERS,
            json={"expected_updated_at": reopened.json()["metadata"]["updated_at"]},
        )
        assert second_zip.status_code == 200
        assert second_zip.content == first_zip.content
        assert ProjectRepository(root).load(project_id) == before

    repository = ProjectRepository(root)
    editor = load_editor_state(repository.load(project_id).state)
    assert editor is not None
    asset = StaticSiteAsset(path=reference, data=repository.read_asset(project_id, reference))
    build = StaticSiteBuilder().build(to_static_site_document(editor, (asset,)))
    expected_zip = StaticSiteExporter().export_zip(build, tmp_path / "expected.zip")
    assert expected_zip.read_bytes() == first_zip.content
    project_directory = next(root.iterdir())
    assert list((project_directory / "site").iterdir()) == []
    assert list((project_directory / "exports").iterdir()) == []
    assert store.calls == 0
