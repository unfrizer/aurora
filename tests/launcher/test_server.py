"""Windows launcher socket, readiness, browser and failure tests."""

from __future__ import annotations

import asyncio
import socket
from pathlib import Path

import pytest
import uvicorn

from src.credentials import WindowsCredentialStore
from src.launcher import run
from src.launcher import server as server_module
from src.preferences import PreferencesStore, default_preferences_path


class FakeStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.reads = 0


class FakeServer:
    def __init__(self, config: uvicorn.Config) -> None:
        self.config = config
        self.started = False
        self.should_exit = False
        self.listener: socket.socket | None = None

    async def serve(self, sockets: list[socket.socket] | None = None) -> None:
        assert sockets is not None and len(sockets) == 1
        self.listener = sockets[0]
        self.started = True
        await asyncio.sleep(0.05)


def _bundle(tmp_path: Path) -> Path:
    root = tmp_path / "frontend" / "dist"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<html>ready</html>", encoding="utf-8")
    return root


def test_prebound_loopback_origin_readiness_and_socket_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(tmp_path)
    instances: list[FakeServer] = []
    opened: list[str] = []

    def make_server(config: uvicorn.Config) -> FakeServer:
        instance = FakeServer(config)
        instances.append(instance)
        return instance

    def open_browser(url: str) -> bool:
        assert instances[0].started
        opened.append(url)
        return True

    monkeypatch.setattr(server_module.uvicorn, "Server", make_server)
    monkeypatch.setattr(server_module.webbrowser, "open", open_browser)
    asyncio.run(
        server_module._serve(  # pyright: ignore[reportPrivateUsage]
            tmp_path / "Projects", bundle, FakeStore()
        )
    )
    instance = instances[0]
    assert instance.listener is not None
    assert instance.listener.fileno() == -1
    assert instance.config.host == "127.0.0.1"
    assert instance.config.port > 0
    assert opened == [f"http://127.0.0.1:{instance.config.port}"]
    assert instance.should_exit
    assert not (tmp_path / "Projects").exists()


@pytest.mark.parametrize("browser_result", [False, RuntimeError("browser unavailable")])
def test_browser_failure_keeps_server_running(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    browser_result: bool | RuntimeError,
) -> None:
    bundle = _bundle(tmp_path)
    instances: list[FakeServer] = []

    def make_server(config: uvicorn.Config) -> FakeServer:
        instance = FakeServer(config)
        instances.append(instance)
        return instance

    def open_browser(_url: str) -> bool:
        if isinstance(browser_result, RuntimeError):
            raise browser_result
        return browser_result

    monkeypatch.setattr(server_module.uvicorn, "Server", make_server)
    monkeypatch.setattr(server_module.webbrowser, "open", open_browser)
    asyncio.run(
        server_module._serve(  # pyright: ignore[reportPrivateUsage]
            tmp_path / "Projects", bundle, FakeStore()
        )
    )
    assert instances[0].started
    assert instances[0].should_exit
    assert "Open the local AURORA UI manually" in caplog.text
    assert "browser unavailable" not in caplog.text


def test_server_exit_before_readiness_fails_without_browser(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(tmp_path)

    class FailedServer(FakeServer):
        async def serve(self, sockets: list[socket.socket] | None = None) -> None:
            assert sockets is not None
            self.listener = sockets[0]

    instances: list[FailedServer] = []

    def make_server(config: uvicorn.Config) -> FailedServer:
        instance = FailedServer(config)
        instances.append(instance)
        return instance

    def unexpected_browser(_url: str) -> bool:
        pytest.fail("Browser opened before server readiness.")

    monkeypatch.setattr(server_module.uvicorn, "Server", make_server)
    monkeypatch.setattr(server_module.webbrowser, "open", unexpected_browser)
    with pytest.raises(RuntimeError, match="did not start"):
        asyncio.run(
            server_module._serve(  # pyright: ignore[reportPrivateUsage]
                tmp_path / "Projects", bundle, FakeStore()
            )
        )
    assert instances[0].listener is not None
    assert instances[0].listener.fileno() == -1


def test_run_rejects_non_windows_before_effect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server_module.sys, "platform", "linux")
    with pytest.raises(SystemExit) as error:
        run()
    assert error.value.code == 1


def test_windows_profile_must_be_absolute_existing_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("USERPROFILE", raising=False)
    with pytest.raises(RuntimeError, match="user profile"):
        server_module._project_root()  # pyright: ignore[reportPrivateUsage]
    monkeypatch.setenv("USERPROFILE", "relative-profile")
    with pytest.raises(RuntimeError, match="user profile"):
        server_module._project_root()  # pyright: ignore[reportPrivateUsage]
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert (
        server_module._project_root()  # pyright: ignore[reportPrivateUsage]
        == tmp_path / "Documents" / "AURORA" / "Projects"
    )


def test_run_uses_validated_bundle_and_fake_credential_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(tmp_path)
    store = FakeStore()
    served: list[tuple[Path, Path, WindowsCredentialStore, PreferencesStore]] = []

    async def fake_serve(
        project_root: Path,
        ui_root: Path,
        credential_store: WindowsCredentialStore,
        preferences_store: PreferencesStore,
    ) -> None:
        served.append((project_root, ui_root, credential_store, preferences_store))

    monkeypatch.setattr(server_module.sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    local_app_data = tmp_path / "LocalAppData"
    local_app_data.mkdir()
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr(server_module, "_ui_root", lambda: bundle)
    monkeypatch.setattr(server_module, "WindowsCredentialStore", lambda: store)
    monkeypatch.setattr(server_module, "_serve", fake_serve)
    run()
    assert len(served) == 1
    assert served[0][:3] == (tmp_path / "Documents" / "AURORA" / "Projects", bundle, store)
    assert served[0][3].load().schema_version == 1
    assert not (local_app_data / "AURORA" / "settings.json").exists()
    assert store.reads == 0


def test_run_missing_bundle_exits_without_credential_or_server(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server_module.sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr(server_module, "_ui_root", lambda: tmp_path / "missing")

    def unexpected_store() -> WindowsCredentialStore:
        pytest.fail("Credential store created for missing UI bundle.")

    monkeypatch.setattr(server_module, "WindowsCredentialStore", unexpected_store)
    with pytest.raises(SystemExit) as error:
        run()
    assert error.value.code == 1


@pytest.mark.parametrize("local_app_data", [None, "relative-local-app-data"])
def test_invalid_local_app_data_fails_before_socket_or_browser(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    local_app_data: str | None,
) -> None:
    bundle = _bundle(tmp_path)
    monkeypatch.setattr(server_module.sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    if local_app_data is None:
        monkeypatch.delenv("LOCALAPPDATA", raising=False)
    else:
        monkeypatch.setenv("LOCALAPPDATA", local_app_data)
    monkeypatch.setattr(server_module, "_ui_root", lambda: bundle)

    def unexpected_effect(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Invalid settings location must not bind or open a browser")

    monkeypatch.setattr(server_module.socket, "socket", unexpected_effect)
    monkeypatch.setattr(server_module.webbrowser, "open", unexpected_effect)
    monkeypatch.setattr(server_module, "WindowsCredentialStore", unexpected_effect)
    with pytest.raises(SystemExit) as error:
        run()
    assert error.value.code == 1
    assert not (tmp_path / "Documents").exists()


def test_default_settings_path_is_passed_without_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(tmp_path)
    local_app_data = tmp_path / "LocalAppData"
    local_app_data.mkdir()
    monkeypatch.setattr(server_module.sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr(server_module, "_ui_root", lambda: bundle)
    observed: list[Path] = []
    real_store = PreferencesStore

    def store_for_test(path: Path) -> PreferencesStore:
        observed.append(path)
        return real_store(path)

    async def fake_serve(
        _projects: Path,
        _bundle: Path,
        _credentials: WindowsCredentialStore,
        _preferences: PreferencesStore,
    ) -> None:
        assert observed == [default_preferences_path()]

    monkeypatch.setattr(server_module, "PreferencesStore", store_for_test)
    monkeypatch.setattr(server_module, "_serve", fake_serve)
    run()
    assert observed == [local_app_data / "AURORA" / "settings.json"]
    assert not observed[0].exists()


def test_run_does_not_read_or_reset_damaged_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(tmp_path)
    local_app_data = tmp_path / "LocalAppData"
    settings_path = local_app_data / "AURORA" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    original = b'{"schema_version":1,"unexpected":"private"}'
    settings_path.write_bytes(original)
    monkeypatch.setattr(server_module.sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr(server_module, "_ui_root", lambda: bundle)
    reached_server = False

    async def fake_serve(
        _projects: Path,
        _bundle: Path,
        _credentials: WindowsCredentialStore,
        _preferences: PreferencesStore,
    ) -> None:
        nonlocal reached_server
        reached_server = True

    monkeypatch.setattr(server_module, "_serve", fake_serve)
    run()
    assert reached_server
    assert settings_path.read_bytes() == original
