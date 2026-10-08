"""Loopback, request-gate, and import-boundary acceptance."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app

_ORIGIN = "http://127.0.0.1:8765"
_PATH = "/api/v1/projects"


class NoopStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        return None

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        return False


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:8765",
        "http://127.0.0.1",
        "https://127.0.0.1:8765",
        "http://127.0.0.1:0",
        "http://127.0.0.1:65536",
        "http://127.0.0.1:8765/path",
        "http://127.0.0.1:8765/",
        "http://evil.example:8765",
    ],
)
def test_app_rejects_noncanonical_origin_without_effect(tmp_path: Path, origin: str) -> None:
    store = NoopStore()
    with pytest.raises(ValueError, match="canonical loopback"):
        create_app(
            project_root=tmp_path / "Projects", credential_store=store, allowed_origin=origin
        )
    assert store.calls == 0
    assert not (tmp_path / "Projects").exists()


def test_app_construction_and_read_only_health_have_no_service_side_effect(
    tmp_path: Path,
) -> None:
    root = tmp_path / "Projects"
    store = NoopStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    assert store.calls == 0
    assert not root.exists()
    with cast(Client, TestClient(app, base_url=_ORIGIN)) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert store.calls == 0
    assert not root.exists()


def test_host_origin_header_and_content_type_gate_before_mutation(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = NoopStore()
    with cast(
        Client,
        TestClient(
            create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN),
            base_url=_ORIGIN,
        ),
    ) as client:
        valid = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
        attempts = [
            client.post(_PATH, json={"name": "Bad"}, headers={"Host": "evil.example", **valid}),
            client.post(_PATH, json={"name": "Bad"}, headers={"X-Aurora-Request": "1"}),
            client.post(
                _PATH, json={"name": "Bad"}, headers={"Origin": "null", "X-Aurora-Request": "1"}
            ),
            client.post(
                _PATH,
                json={"name": "Bad"},
                headers={"Origin": "https://evil.example", "X-Aurora-Request": "1"},
            ),
            client.post(_PATH, json={"name": "Bad"}, headers={"Origin": _ORIGIN}),
            client.post(
                _PATH,
                content='{"name":"Bad"}',
                headers={**valid, "Content-Type": "text/plain"},
            ),
            client.post(
                _PATH,
                content='{"name":"Bad"}',
                headers={**valid, "Content-Type": "application/json", "Content-Length": "bad"},
            ),
        ]
        assert all(
            item.status_code == 400 and item.json() == {"error": {"code": 400}} for item in attempts
        )
        assert client.get(_PATH).json() == []
        assert client.delete("/api/v1/projects/not-a-uuid").status_code == 400
        assert client.get("/api/v1/health", headers={"Host": "evil.example"}).status_code == 400
        foreign = client.get("/api/v1/health", headers={"Origin": "https://evil.example"})
        assert foreign.status_code == 200
        assert "access-control-allow-origin" not in foreign.headers
    assert store.calls == 0
    assert not root.exists()


def test_oversized_body_is_rejected_before_project_creation(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    app = create_app(project_root=root, credential_store=NoopStore(), allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN)) as client:
        response = client.post(
            _PATH,
            content=b'{"name":"' + b"x" * (2 * 1024 * 1024) + b'"}',
            headers={
                "Origin": _ORIGIN,
                "X-Aurora-Request": "1",
                "Content-Type": "application/json",
            },
        )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert not root.exists()


def test_p6_imports_only_approved_application_gateways() -> None:
    allowed = {
        "src.credentials",
        "src.generation",
        "src.local_api",
        "src.local_api.app",
        "src.local_api.schemas",
        "src.projects",
    }
    for path in Path("src/local_api").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("starlette."), (path, node.module)
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("src."):
                assert node.module in allowed, (path, node.module)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("starlette."), (path, alias.name)
                    if alias.name.startswith("src."):
                        assert alias.name in allowed, (path, alias.name)
    for path in Path("src").rglob("*.py"):
        if "local_api" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            (
                isinstance(node, ast.ImportFrom)
                and node.module is not None
                and node.module.startswith("src.local_api")
            )
            or (
                isinstance(node, ast.Import)
                and any(alias.name.startswith("src.local_api") for alias in node.names)
            )
            for node in ast.walk(tree)
        ), path
