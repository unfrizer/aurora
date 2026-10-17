"""Public P1 → P7 → P4 → P6 folder export survives a local app reopen."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.editor import load_editor_state, to_static_site_document
from src.local_api import create_app
from src.projects import ProjectRepository
from src.site_export import StaticSiteAsset, StaticSiteBuilder, StaticSiteExporter

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-integration-folder"


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


def _files(folder: Path) -> dict[str, bytes]:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file()
    }


def test_create_upload_save_folder_reopen_and_match_p4(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = EmptyStore()
    first_app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(first_app, base_url=_ORIGIN)) as client:
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
        route = f"/api/v1/projects/{project_id}/exports/folder"
        first_export = client.post(
            route,
            headers=_HEADERS,
            json={"expected_updated_at": timestamp, "confirm_export": True},
        )
        assert first_export.status_code == 201
        first_folder = Path(first_export.json()["folder_path"])
        preview = client.get(f"/api/v1/projects/{project_id}/preview/index.html")
        assert preview.status_code == 200
        assert (first_folder / "index.html").read_bytes() == preview.content
        before = ProjectRepository(root).load(project_id)

    second_app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second_app, base_url=_ORIGIN)) as client:
        reopened = client.get(f"/api/v1/projects/{project_id}")
        assert reopened.status_code == 200
        assert reopened.json()["state"]["editor"] == _editor(reference)
        second_export = client.post(
            route,
            headers=_HEADERS,
            json={
                "expected_updated_at": reopened.json()["metadata"]["updated_at"],
                "confirm_export": True,
            },
        )
        assert second_export.status_code == 201
        second_folder = Path(second_export.json()["folder_path"])
        assert first_folder != second_folder
        assert _files(first_folder) == _files(second_folder)
        assert ProjectRepository(root).load(project_id) == before

    repository = ProjectRepository(root)
    editor = load_editor_state(repository.load(project_id).state)
    assert editor is not None
    asset = StaticSiteAsset(path=reference, data=repository.read_asset(project_id, reference))
    build = StaticSiteBuilder().build(to_static_site_document(editor, (asset,)))
    direct = StaticSiteExporter().export_folder(build, tmp_path / "direct")
    assert _files(first_folder) == _files(direct)
    assert _files(first_folder)[reference] == _IMAGE
    assert first_folder.parent == second_folder.parent == repository.export_directory(project_id)
    assert list((first_folder.parent.parent / "site").iterdir()) == []
    assert store.calls == 0
