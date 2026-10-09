"""Same-origin static UI and P6 coexistence tests."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.launcher import create_desktop_app

_ORIGIN = "http://127.0.0.1:8765"


class FakeStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.reads = 0

    def get_secret(self, name: SecretName) -> str | None:
        self.reads += 1
        return None


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    root = tmp_path / "frontend" / "dist"
    (root / "assets" / "nested").mkdir(parents=True)
    (root / "index.html").write_text("<html>AURORA</html>", encoding="utf-8")
    (root / "assets" / "app.js").write_text("export const ready = true;", encoding="utf-8")
    (root / "assets" / "nested" / "app.css").write_text("body{}", encoding="utf-8")
    (root / "assets" / "app.js.map").write_text("private", encoding="utf-8")
    (root / "assets" / "active.svg").write_text("<svg></svg>", encoding="utf-8")
    return root


@pytest.fixture
def desktop(bundle: Path, tmp_path: Path) -> Iterator[tuple[Client, FakeStore, Path]]:
    projects = tmp_path / "Projects"
    store = FakeStore()
    app = create_desktop_app(
        project_root=projects, credential_store=store, allowed_origin=_ORIGIN, ui_root=bundle
    )
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield client, store, projects


def test_gateway_and_static_get_head(desktop: tuple[Client, FakeStore, Path]) -> None:
    from src import launcher

    assert launcher.__all__ == ["create_desktop_app", "run"]
    client, store, projects = desktop
    index = client.get("/")
    assert index.status_code == 200
    assert index.text == "<html>AURORA</html>"
    assert index.headers["content-type"].startswith("text/html")
    assert index.headers["cache-control"] == "no-store"
    assert index.headers["x-content-type-options"] == "nosniff"
    assert index.headers["referrer-policy"] == "no-referrer"
    head = client.head("/")
    assert head.status_code == 200
    assert head.content == b""
    assert head.headers["content-length"] == index.headers["content-length"]
    assert client.get("/assets/app.js").text == "export const ready = true;"
    assert client.get("/assets/nested/app.css").headers["content-type"].startswith("text/css")
    asset_head = client.head("/assets/app.js")
    assert asset_head.content == b""
    assert (
        asset_head.headers["content-length"]
        == client.get("/assets/app.js").headers["content-length"]
    )
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert not projects.exists()
    assert store.reads == 0


def test_launcher_imports_only_owned_files_and_public_project_gateways() -> None:
    launcher_root = Path(__file__).resolve().parents[2] / "src" / "launcher"
    allowed = {"src.credentials", "src.local_api", "src.launcher"}
    for file in launcher_root.glob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                if node.module.startswith("src."):
                    assert any(
                        node.module == name or node.module.startswith(f"{name}.")
                        for name in allowed
                    )
                    assert not node.module.startswith(("src.credentials.", "src.local_api."))
            elif isinstance(node, ast.Import):
                assert all(
                    not item.name.startswith("src.")
                    or item.name in allowed
                    or item.name.startswith("src.launcher.")
                    for item in node.names
                )


def test_p6_host_and_mutation_gates_remain_active(desktop: tuple[Client, FakeStore, Path]) -> None:
    client, _store, projects = desktop
    assert client.get("/", headers={"Host": "not-local.invalid"}).status_code == 400
    assert client.get("/api/v1/health", headers={"Host": "not-local.invalid"}).status_code == 400
    assert client.post("/api/v1/projects", json={"name": "No origin"}).status_code == 400
    assert (
        client.post(
            "/api/v1/projects", headers={"Origin": _ORIGIN}, json={"name": "No header"}
        ).status_code
        == 400
    )
    assert not projects.exists()
    created = client.post(
        "/api/v1/projects",
        headers={"Origin": _ORIGIN, "X-Aurora-Request": "1"},
        json={"name": "Local"},
    )
    assert created.status_code == 201
    assert len(client.get("/api/v1/projects").json()) == 1


@pytest.mark.parametrize(
    "path",
    [
        "/assets/../index.html",
        "/assets/%2e%2e/index.html",
        "/assets/nested%2Fapp.css",
        "/assets/app.js.map",
        "/assets/active.svg",
        "/assets/missing.js",
        "/assets/.hidden.js",
        "/favicon.ico",
        "/projects/aurora.project.json",
    ],
)
def test_nonapproved_paths_are_not_served(
    desktop: tuple[Client, FakeStore, Path], path: str
) -> None:
    client, _store, _projects = desktop
    response = client.get(path)
    assert response.status_code == 404
    assert response.json() == {"error": {"code": 404}}
    assert path not in response.text


def test_missing_or_linked_bundle_is_rejected(
    bundle: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = FakeStore()
    with pytest.raises(RuntimeError, match="built AURORA UI"):
        create_desktop_app(
            project_root=tmp_path / "Projects",
            credential_store=store,
            allowed_origin=_ORIGIN,
            ui_root=tmp_path / "missing",
        )
    from src.launcher import desktop as desktop_module

    original = desktop_module._is_reparse  # pyright: ignore[reportPrivateUsage]

    def linked_index(path: Path) -> bool:
        return path == bundle / "index.html" or original(path)

    monkeypatch.setattr(desktop_module, "_is_reparse", linked_index)
    with pytest.raises(RuntimeError, match="built AURORA UI"):
        create_desktop_app(
            project_root=tmp_path / "Projects",
            credential_store=store,
            allowed_origin=_ORIGIN,
            ui_root=bundle,
        )


def test_asset_link_is_rejected_after_factory(
    desktop: tuple[Client, FakeStore, Path], bundle: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.launcher import desktop as desktop_module

    client, _store, _projects = desktop
    original = desktop_module._is_reparse  # pyright: ignore[reportPrivateUsage]
    linked = bundle / "assets" / "app.js"

    def linked_asset(path: Path) -> bool:
        return path == linked or original(path)

    monkeypatch.setattr(desktop_module, "_is_reparse", linked_asset)
    assert client.get("/assets/app.js").status_code == 404
