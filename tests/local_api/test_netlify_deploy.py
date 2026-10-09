"""P6-005 explicit Netlify HTTP composition with no real network."""

from __future__ import annotations

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.core.types import JSONDict
from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.deployment import NetlifyDeployer, NetlifyDeployError, NetlifyDeployment
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository
from src.site_export import StaticSiteBuild, StaticSiteBuilder, StaticSiteDocument

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_SITE_ID = "12345678-1234-1234-1234-123456789abc"
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-deploy"
type _Stage = Literal["validation", "site_create", "upload", "poll"]
type _Category = Literal[
    "invalid_input", "auth", "rate_limit", "remote", "transport", "protocol", "failed", "timeout"
]


class FakeStore(WindowsCredentialStore):
    def __init__(self, token: str | None = "test-netlify-token") -> None:
        self.token = token
        self.calls: list[SecretName] = []
        self.native_failure = False

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls.append(name)
        if self.native_failure:
            raise CredentialStoreError("C:\\private\\credential")
        assert name == "netlify_token"
        return self.token

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("Unexpected credential delete")


@dataclass(frozen=True)
class DeployAPI:
    client: Client
    root: Path
    store: FakeStore


@pytest.fixture
def api(tmp_path: Path) -> DeployAPI:
    root = tmp_path / "Projects"
    store = FakeStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    client = cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False))
    return DeployAPI(client, root, store)


@pytest.fixture(autouse=True)
def block_unexpected_live_deploy(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    calls = 0

    def forbidden(
        _deployer: NetlifyDeployer, _build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        nonlocal calls
        calls += 1
        raise AssertionError("Unexpected P5 network boundary")

    monkeypatch.setattr(NetlifyDeployer, "deploy", forbidden)
    yield
    assert calls == 0


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
                "meta_description": "Тест",
                "heading": "Локальный деплой",
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


def _create(api: DeployAPI) -> tuple[str, str]:
    created = api.client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Студия"})
    assert created.status_code == 201
    metadata = created.json()["metadata"]
    return metadata["project_id"], metadata["updated_at"]


def _save(api: DeployAPI, project_id: str, timestamp: str, editor: dict[str, object]) -> str:
    saved = api.client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={"editor": editor, "expected_updated_at": timestamp},
    )
    assert saved.status_code == 200
    return saved.json()["metadata"]["updated_at"]


def _route(project_id: str) -> str:
    return f"/api/v1/projects/{project_id}/deployments/netlify"


def _body(timestamp: str, site_id: str | None = None) -> dict[str, object]:
    return {"expected_updated_at": timestamp, "confirm_deploy": True, "site_id": site_id}


def test_new_site_success_uses_typed_build_without_project_mutation(
    api: DeployAPI, monkeypatch: pytest.MonkeyPatch
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
        content=b"\x89PNG\r\n\x1a\nunused",
    )
    assert unused.status_code == 201
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    before = ProjectRepository(api.root).load(project_id)
    calls: list[tuple[StaticSiteBuild, str | None]] = []
    tokens: list[str] = []
    reads: list[str] = []
    original_read = ProjectRepository.read_asset
    original_init = NetlifyDeployer.__init__

    def observe_init(deployer: NetlifyDeployer, api_token: str) -> None:
        tokens.append(api_token)
        original_init(deployer, api_token)

    def observe_read(repository: ProjectRepository, identifier: str, path: str) -> bytes:
        reads.append(path)
        return original_read(repository, identifier, path)

    def fake_deploy(
        deployer: NetlifyDeployer, build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        calls.append((build, site_id))
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(api.client.get, f"/api/v1/projects/{project_id}")
            assert future.result(timeout=5).status_code == 200
        return NetlifyDeployment(
            site_id=_SITE_ID,
            deploy_id="deploy_1",
            public_url="https://example.netlify.app",
        )

    monkeypatch.setattr(ProjectRepository, "read_asset", observe_read)
    monkeypatch.setattr(NetlifyDeployer, "__init__", observe_init)
    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)
    response = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 200
    assert response.json() == {
        "site_id": _SITE_ID,
        "deploy_id": "deploy_1",
        "public_url": "https://example.netlify.app",
    }
    assert "access-control-allow-origin" not in response.headers
    assert api.store.calls == ["netlify_token"]
    assert len(calls) == 1
    assert tokens == ["test-netlify-token"]
    assert calls[0][1] is None
    assert reads == [reference]
    files = {item.path: item.data for item in calls[0][0].files}
    assert files[reference] == _IMAGE
    assert "Локальный деплой" in files["index.html"].decode("utf-8")
    assert ProjectRepository(api.root).load(project_id) == before
    project_directory = next(api.root.iterdir())
    assert list((project_directory / "site").iterdir()) == []
    assert list((project_directory / "exports").iterdir()) == []


def test_existing_site_id_passes_exactly_once(
    api: DeployAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    seen: list[str | None] = []

    def fake_deploy(
        _deployer: NetlifyDeployer, _build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        seen.append(site_id)
        return NetlifyDeployment(
            site_id=_SITE_ID, deploy_id="deploy_2", public_url="https://example.netlify.app"
        )

    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)
    response = api.client.post(
        _route(project_id), headers=_HEADERS, json=_body(timestamp, _SITE_ID)
    )
    assert response.status_code == 200
    assert response.json()["deploy_id"] == "deploy_2"
    assert seen == [_SITE_ID]


def test_request_shape_and_same_origin_gate_precede_credential_and_network(
    api: DeployAPI,
) -> None:
    project_id, timestamp = _create(api)
    route = _route(project_id)
    malformed: tuple[dict[str, object], ...] = (
        {},
        {"expected_updated_at": timestamp},
        {"expected_updated_at": timestamp, "confirm_deploy": False},
        {"expected_updated_at": timestamp, "confirm_deploy": 1},
        {**_body(timestamp), "token": "leak"},
        _body(timestamp, "ABCDEFAB-1234-1234-1234-123456789ABC"),
        _body(timestamp, "not-a-uuid"),
    )
    for body in malformed:
        response = api.client.post(route, headers=_HEADERS, json=body)
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
    for headers in (
        {"Host": "evil", **_HEADERS},
        {"Origin": "https://evil.example", "X-Aurora-Request": "1"},
        {"Origin": _ORIGIN},
    ):
        response = api.client.post(route, headers=headers, json=_body(timestamp))
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
    non_json = api.client.post(
        route, headers={**_HEADERS, "Content-Type": "text/plain"}, content=b"{}"
    )
    assert non_json.status_code == 400
    oversized = api.client.post(
        route,
        headers=_HEADERS,
        json={**_body(timestamp), "expected_updated_at": "x" * (2 * 1024 * 1024)},
    )
    assert oversized.status_code == 400
    invalid_project = api.client.post(_route("bad-id"), headers=_HEADERS, json=_body(timestamp))
    assert invalid_project.status_code == 400
    missing_project = api.client.post(
        _route("00000000-0000-0000-0000-000000000000"),
        headers=_HEADERS,
        json=_body(timestamp),
    )
    assert missing_project.status_code == 404
    assert missing_project.json() == {"error": {"code": 404}}
    assert api.store.calls == []


def test_stale_and_missing_token_short_circuit_before_build(
    api: DeployAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    current = _save(api, project_id, timestamp, _editor())

    def forbidden_build(
        _builder: StaticSiteBuilder, _document: StaticSiteDocument
    ) -> StaticSiteBuild:
        raise AssertionError("Unexpected build")

    monkeypatch.setattr(StaticSiteBuilder, "build", forbidden_build)
    stale = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}
    assert api.store.calls == []
    api.store.token = None
    missing = api.client.post(_route(project_id), headers=_HEADERS, json=_body(current))
    assert missing.status_code == 409
    assert missing.json() == {"error": {"code": 409}}
    assert api.store.calls == ["netlify_token"]


@pytest.mark.parametrize("editor", [None, {"schema_version": 2}, {**_editor(), "pages": []}])
def test_invalid_editor_or_draft_is_400(api: DeployAPI, editor: object) -> None:
    project_id, _timestamp = _create(api)
    repository = ProjectRepository(api.root)
    current = repository.load(project_id)
    saved = repository.save(
        ProjectDocument(metadata=current.metadata, state=cast("JSONDict", {"editor": editor}))
    )
    response = api.client.post(
        _route(project_id),
        headers=_HEADERS,
        json=_body(saved.metadata.updated_at),
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert repository.load(project_id) == saved


@pytest.mark.parametrize("reference", [f"assets/{'a' * 64}.png", "../private.png"])
def test_bad_referenced_asset_is_400(api: DeployAPI, reference: str) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    response = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "private" not in response.text


def test_corrupt_asset_and_native_p1_read_are_sanitized(
    api: DeployAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, timestamp = _create(api)
    uploaded = api.client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": "image/png"},
        content=_IMAGE,
    )
    assert uploaded.status_code == 201
    reference = uploaded.json()["path"]
    timestamp = _save(api, project_id, timestamp, _editor(reference))
    target = next(api.root.iterdir()) / reference
    target.write_bytes(b"\x89PNG\r\n\x1a\ncorrupt")
    corrupt = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert corrupt.status_code == 400
    assert corrupt.json() == {"error": {"code": 400}}

    def fail_read(_repository: ProjectRepository, _identifier: str, _path: str) -> bytes:
        raise OSError("C:\\private\\asset")

    monkeypatch.setattr(ProjectRepository, "read_asset", fail_read)
    native = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert native.status_code == 500
    assert native.json() == {"error": {"code": 500}}
    assert "private" not in native.text


def test_native_credential_and_server_token_failures_are_sanitized(
    api: DeployAPI,
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    api.store.native_failure = True
    native = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert native.status_code == 503
    assert native.json() == {"error": {"code": 503}}
    assert "private" not in native.text
    api.store.native_failure = False
    api.store.token = "\n"
    invalid_token = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert invalid_token.status_code == 500
    assert invalid_token.json() == {"error": {"code": 500}}


@pytest.mark.parametrize(
    ("stage", "category", "expected_status"),
    [
        ("site_create", "auth", 502),
        ("upload", "remote", 502),
        ("poll", "protocol", 502),
        ("poll", "failed", 502),
        ("upload", "rate_limit", 503),
        ("poll", "transport", 503),
        ("poll", "timeout", 504),
        ("validation", "invalid_input", 500),
    ],
)
def test_p5_errors_without_ids_keep_original_envelope(
    api: DeployAPI,
    monkeypatch: pytest.MonkeyPatch,
    stage: _Stage,
    category: _Category,
    expected_status: int,
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())
    failure = NetlifyDeployError(stage, category)
    calls = 0

    def fake_deploy(
        _deployer: NetlifyDeployer, _build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        nonlocal calls
        calls += 1
        raise failure

    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)
    response = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == expected_status
    assert response.json() == {"error": {"code": expected_status}}
    assert calls == 1
    assert "test-netlify-token" not in response.text


@pytest.mark.parametrize(("site_id", "deploy_id"), [(_SITE_ID, None), (_SITE_ID, "deploy_1")])
def test_partial_failure_returns_only_validated_recovery_ids(
    api: DeployAPI,
    monkeypatch: pytest.MonkeyPatch,
    site_id: str,
    deploy_id: str | None,
) -> None:
    project_id, timestamp = _create(api)
    timestamp = _save(api, project_id, timestamp, _editor())

    def fake_deploy(
        _deployer: NetlifyDeployer, _build: StaticSiteBuild, *, site_id: str | None = None
    ) -> NetlifyDeployment:
        raise NetlifyDeployError("poll", "timeout", _SITE_ID, deploy_id)

    monkeypatch.setattr(NetlifyDeployer, "deploy", fake_deploy)
    response = api.client.post(_route(project_id), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 504
    assert response.json() == {
        "error": {
            "code": 504,
            "recovery": {"site_id": site_id, "deploy_id": deploy_id},
        }
    }
    assert "test-netlify-token" not in response.text
    assert "access-control-allow-origin" not in response.headers
    old_route = api.client.get(f"/api/v1/projects/{project_id}/preview/index.html")
    assert old_route.status_code == 200
    old_failure = api.client.get(f"/api/v1/projects/{project_id}/preview/unknown.html")
    assert old_failure.json() == {"error": {"code": 404}}
