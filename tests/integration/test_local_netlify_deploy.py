"""P1 → P7 → P4 → P6 explicit deploy composition with fake P5."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.deployment import NetlifyDeployer, NetlifyDeployment
from src.editor import load_editor_state, to_static_site_document
from src.local_api import create_app
from src.projects import ProjectRepository
from src.site_export import StaticSiteAsset, StaticSiteBuild, StaticSiteBuilder

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_SITE_ID = "12345678-1234-1234-1234-123456789abc"
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-integration-deploy"


class FakeStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls: list[SecretName] = []

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls.append(name)
        assert name == "netlify_token"
        return "integration-test-token"

    def delete_secret(self, name: SecretName) -> bool:
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
                "heading": "Deploy snapshot",
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


def test_create_upload_save_deploy_reopen_and_redeploy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Projects"
    store = FakeStore()
    calls: list[tuple[StaticSiteBuild, str | None]] = []

    def fake_deploy(
        _deployer: NetlifyDeployer, build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        calls.append((build, site_id))
        return NetlifyDeployment(
            site_id=_SITE_ID,
            deploy_id=f"deploy_{len(calls)}",
            public_url="https://example.netlify.app",
        )

    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)
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
        route = f"/api/v1/projects/{project_id}/deployments/netlify"
        deployed = client.post(
            route,
            headers=_HEADERS,
            json={
                "expected_updated_at": saved.json()["metadata"]["updated_at"],
                "confirm_deploy": True,
            },
        )
        assert deployed.status_code == 200
        assert deployed.json() == {
            "site_id": _SITE_ID,
            "deploy_id": "deploy_1",
            "public_url": "https://example.netlify.app",
        }
        before = ProjectRepository(root).load(project_id)

    second = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        reopened = client.get(f"/api/v1/projects/{project_id}")
        assert reopened.status_code == 200
        assert reopened.json()["state"]["editor"] == _editor(reference)
        redeployed = client.post(
            route,
            headers=_HEADERS,
            json={
                "expected_updated_at": reopened.json()["metadata"]["updated_at"],
                "confirm_deploy": True,
                "site_id": _SITE_ID,
            },
        )
        assert redeployed.status_code == 200
        assert redeployed.json()["deploy_id"] == "deploy_2"
        assert ProjectRepository(root).load(project_id) == before

    repository = ProjectRepository(root)
    editor = load_editor_state(repository.load(project_id).state)
    assert editor is not None
    asset = StaticSiteAsset(path=reference, data=repository.read_asset(project_id, reference))
    expected = StaticSiteBuilder().build(to_static_site_document(editor, (asset,)))
    assert calls == [(expected, None), (expected, _SITE_ID)]
    project_directory = next(root.iterdir())
    assert list((project_directory / "site").iterdir()) == []
    assert list((project_directory / "exports").iterdir()) == []
    assert store.calls == ["netlify_token", "netlify_token"]
