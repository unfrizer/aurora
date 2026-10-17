"""One offline local-app journey through existing public composition boundaries."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import cast
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient
from httpx import Client

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
from src.projects import ProjectRepository
from src.site_export import StaticSiteBuild

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_PNG = b"\x89PNG\r\n\x1a\nsynthetic-mvp-image"
_SITE_ID = "12345678-1234-1234-1234-123456789abc"


class _FakeCredentials(WindowsCredentialStore):
    def __init__(self) -> None:
        self.reads: list[SecretName] = []

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No credential write in acceptance test")

    def get_secret(self, name: SecretName) -> str | None:
        self.reads.append(name)
        return "synthetic-key"

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No credential delete in acceptance test")


def test_local_first_use_to_reopen_export_and_fake_deploy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ui_root = tmp_path / "frontend" / "dist"
    (ui_root / "assets").mkdir(parents=True)
    (ui_root / "index.html").write_text("<html>AURORA test shell</html>", encoding="utf-8")
    (ui_root / "assets" / "app.js").write_text("export {};", encoding="utf-8")
    project_root = tmp_path / "Projects"
    settings_path = tmp_path / "Settings" / "settings.json"
    credentials = _FakeCredentials()
    text_calls: list[GenerationRequest] = []
    image_calls: list[ImageGenerationRequest] = []
    deploy_calls: list[tuple[StaticSiteBuild, str | None]] = []

    def fake_text(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        text_calls.append(request)
        return GenerationJob(
            job_id="mvp-text-job",
            request=request,
            status="completed",
            result=GenerationResult(
                response_id="mvp-text-response",
                model=request.model,
                output_text=json.dumps(
                    {
                        "brand": {
                            "name": "Studio",
                            "tagline": "Thoughtful design",
                            "primary_color": "#123456",
                            "secondary_color": "#abcdef",
                            "font_family": "system",
                        },
                        "pages": [
                            {
                                "slug": "index",
                                "title": "Studio Home",
                                "meta_description": "A design studio",
                                "heading": "Welcome",
                                "sections": [{"heading": "Services", "body": "Our design work"}],
                            }
                        ],
                    }
                ),
            ),
        )

    def fake_image(
        _client: OpenAIImageClient, request: ImageGenerationRequest
    ) -> ImageGenerationJob:
        image_calls.append(request)
        return ImageGenerationJob(
            "a0000000-0000-4000-8000-000000000002",
            request,
            "completed",
            result=ImageGenerationResult(_PNG),
        )

    def fake_deploy(
        _deployer: NetlifyDeployer, build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        deploy_calls.append((build, site_id))
        return NetlifyDeployment(
            site_id=_SITE_ID,
            deploy_id="mvp-fake-deploy",
            public_url="https://example.netlify.app",
        )

    monkeypatch.setattr(OpenAIResponsesClient, "generate", fake_text)
    monkeypatch.setattr(OpenAIImageClient, "generate", fake_image)
    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)

    def app_client() -> Client:
        app = create_desktop_app(
            project_root=project_root,
            credential_store=credentials,
            allowed_origin=_ORIGIN,
            ui_root=ui_root,
            preferences_store=PreferencesStore(settings_path),
        )
        return cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False))

    with app_client() as first:
        assert first.get("/").text == "<html>AURORA test shell</html>"
        initial = first.get("/api/v1/preferences")
        assert initial.status_code == 200
        assert initial.json()["preferences"]["language"] is None
        assert initial.json()["projects_directory"] == str(project_root)
        assert not settings_path.exists()
        assert not project_root.exists()

        chosen = {
            **initial.json()["preferences"],
            "language": "en",
            "general_model": "configured-text-model",
            "image_model": "configured-image-model",
            "onboarding_completed": True,
        }
        denied = first.put(
            "/api/v1/preferences",
            headers={"Origin": "http://evil.example", "X-Aurora-Request": "1"},
            json={"preferences": chosen, "expected_revision": initial.json()["revision"]},
        )
        assert denied.status_code == 400
        assert not settings_path.exists()
        saved_preferences = first.put(
            "/api/v1/preferences",
            headers=_HEADERS,
            json={"preferences": chosen, "expected_revision": initial.json()["revision"]},
        )
        assert saved_preferences.status_code == 200
        assert saved_preferences.json()["preferences"] == chosen
        assert settings_path.is_file()
        assert "synthetic-key" not in settings_path.read_text(encoding="utf-8")
        assert not project_root.exists()

        created = first.post("/api/v1/projects", headers=_HEADERS, json={"name": "Studio"})
        assert created.status_code == 201
        project_id = created.json()["metadata"]["project_id"]
        source_updated_at = created.json()["metadata"]["updated_at"]
        draft = first.post(
            f"/api/v1/projects/{project_id}/generation/draft",
            headers=_HEADERS,
            json={
                "business_prompt": "Make a studio site",
                "language": "en",
                "model": chosen["general_model"],
                "expected_updated_at": source_updated_at,
                "confirm_generation": True,
            },
        )
        assert draft.status_code == 200
        assert draft.json()["status"] == "completed"
        assert draft.json()["source_updated_at"] == source_updated_at
        assert len(text_calls) == 1
        assert text_calls[0].model == "configured-text-model"
        assert first.get(f"/api/v1/projects/{project_id}").json()["state"] == {}

        candidate = draft.json()["editor"]
        accepted = first.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={"editor": candidate, "expected_updated_at": source_updated_at},
        )
        assert accepted.status_code == 200
        assert accepted.json()["state"]["editor"] == candidate
        saved_at = accepted.json()["metadata"]["updated_at"]

        image = first.post(
            f"/api/v1/projects/{project_id}/generation/image",
            headers=_HEADERS,
            json={
                "prompt": "A calm studio scene",
                "model": chosen["image_model"],
                "expected_updated_at": saved_at,
                "confirm_generation": True,
            },
        )
        assert image.status_code == 200
        assert image.json()["status"] == "completed"
        assert len(image_calls) == 1
        assert image_calls[0].model == "configured-image-model"
        asset_path = image.json()["asset_path"]
        assert first.get(f"/api/v1/projects/{project_id}/{asset_path}").content == _PNG
        assert first.get(f"/api/v1/projects/{project_id}").json()["state"]["editor"] == candidate

        edited = json.loads(json.dumps(candidate))
        edited["pages"][0]["sections"][0]["image_path"] = asset_path
        edited["pages"][0]["sections"][0]["image_alt"] = "Studio scene"
        edited["brand"]["tagline"] = "Edited by user"
        attached = first.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={"editor": edited, "expected_updated_at": saved_at},
        )
        assert attached.status_code == 200
        final_stamp = attached.json()["metadata"]["updated_at"]
        route = f"/api/v1/projects/{project_id}"
        preview = first.get(f"{route}/preview/index.html")
        assert preview.status_code == 200
        assert b"Edited by user" in preview.content
        assert b"Studio scene" in preview.content

        zip_response = first.post(
            f"{route}/exports/zip",
            headers=_HEADERS,
            json={"expected_updated_at": final_stamp},
        )
        assert zip_response.status_code == 200
        with ZipFile(BytesIO(zip_response.content)) as archive:
            members = set(archive.namelist())
            assert members == {"index.html", "assets/site.css", asset_path}
            assert archive.read("index.html") == preview.content
            assert archive.read(asset_path) == _PNG
            assert "state.json" not in members
            assert "aurora.project.json" not in members

        folder_response = first.post(
            f"{route}/exports/folder",
            headers=_HEADERS,
            json={"expected_updated_at": final_stamp, "confirm_export": True},
        )
        assert folder_response.status_code == 201
        export_folder = Path(folder_response.json()["folder_path"])
        assert export_folder.is_relative_to(project_root)
        assert (export_folder / "index.html").read_bytes() == preview.content
        assert (export_folder / asset_path).read_bytes() == _PNG
        assert settings_path.parent != export_folder.parent

        deployed = first.post(
            f"{route}/deployments/netlify",
            headers=_HEADERS,
            json={"expected_updated_at": final_stamp, "confirm_deploy": True},
        )
        assert deployed.status_code == 200
        assert deployed.json()["public_url"] == "https://example.netlify.app"
        assert len(deploy_calls) == 1
        assert deploy_calls[0][1] is None

    with app_client() as reopened:
        preferences = reopened.get("/api/v1/preferences")
        assert preferences.status_code == 200
        assert preferences.json()["preferences"] == chosen
        assert preferences.json()["revision"] == saved_preferences.json()["revision"]
        project = reopened.get(f"/api/v1/projects/{project_id}")
        assert project.status_code == 200
        assert project.json()["state"]["editor"] == edited
        assert project.json()["metadata"]["updated_at"] == final_stamp
        reopened_preview = reopened.get(f"/api/v1/projects/{project_id}/preview/index.html")
        assert reopened_preview.content == preview.content
    assert ProjectRepository(project_root).read_asset(project_id, asset_path) == _PNG
    assert credentials.reads == ["openai_api_key", "openai_api_key", "netlify_token"]
