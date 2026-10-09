"""Built UI and existing project API share one local origin."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

import pytest
import uvicorn
from fastapi.testclient import TestClient
from httpx import AsyncClient, Client

from src.credentials import SecretName, WindowsCredentialStore
from src.launcher import create_desktop_app
from src.launcher import server as launcher_server

_ORIGIN = "http://127.0.0.1:8765"


class FakeStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.reads = 0

    def get_secret(self, name: SecretName) -> str | None:
        self.reads += 1
        return None


def test_ui_and_project_reopen_share_one_origin_without_real_secrets(tmp_path: Path) -> None:
    ui_root = tmp_path / "frontend" / "dist"
    (ui_root / "assets").mkdir(parents=True)
    (ui_root / "index.html").write_text("<html>AURORA</html>", encoding="utf-8")
    (ui_root / "assets" / "app.js").write_text("export {};", encoding="utf-8")
    project_root = tmp_path / "Projects"
    store = FakeStore()

    def client() -> TestClient:
        app = create_desktop_app(
            project_root=project_root,
            credential_store=store,
            allowed_origin=_ORIGIN,
            ui_root=ui_root,
        )
        return TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)

    with cast(Client, client()) as first:
        assert first.get("/").status_code == 200
        assert first.get("/assets/app.js").status_code == 200
        created = first.post(
            "/api/v1/projects",
            headers={"Origin": _ORIGIN, "X-Aurora-Request": "1"},
            json={"name": "Local Project"},
        )
        assert created.status_code == 201
        project_id = created.json()["metadata"]["project_id"]
    with cast(Client, client()) as second:
        assert second.get(f"/api/v1/projects/{project_id}").json() == created.json()
        assert second.get("/").text == "<html>AURORA</html>"
        assert second.get("/state.json").status_code == 404
        assert second.get("/aurora.project.json").status_code == 404
    assert store.reads == 0


@pytest.mark.asyncio
async def test_real_loopback_socket_serves_ui_and_api_without_browser_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ui_root = tmp_path / "frontend" / "dist"
    (ui_root / "assets").mkdir(parents=True)
    (ui_root / "index.html").write_text("<html>real socket</html>", encoding="utf-8")
    store = FakeStore()
    ready = asyncio.Event()
    servers: list[uvicorn.Server] = []
    opened: list[str] = []
    actual_server_type = uvicorn.Server

    def make_server(config: uvicorn.Config) -> uvicorn.Server:
        instance = actual_server_type(config)
        servers.append(instance)
        return instance

    def fake_browser(url: str) -> bool:
        opened.append(url)
        ready.set()
        return True

    monkeypatch.setattr(launcher_server.uvicorn, "Server", make_server)
    monkeypatch.setattr(launcher_server.webbrowser, "open", fake_browser)
    running = asyncio.create_task(
        launcher_server._serve(  # pyright: ignore[reportPrivateUsage]
            tmp_path / "Projects", ui_root, store
        )
    )
    try:
        await asyncio.wait_for(ready.wait(), timeout=10)
        async with AsyncClient(base_url=opened[0], timeout=3) as client:
            index = await client.get("/")
            health = await client.get("/api/v1/health")
            assert index.status_code == 200
            assert index.text == "<html>real socket</html>"
            assert health.json() == {"status": "ok"}
        assert servers[0].started
        assert store.reads == 0
        assert not (tmp_path / "Projects").exists()
    finally:
        if servers:
            servers[0].should_exit = True
        await asyncio.wait_for(running, timeout=10)
