"""Foreground Windows loopback server and browser startup."""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import sys
import webbrowser
from pathlib import Path

import uvicorn

from src.credentials import WindowsCredentialStore
from src.launcher.desktop import create_desktop_app, validate_bundle

_LOGGER = logging.getLogger("aurora.launcher")
_HOST = "127.0.0.1"


def _project_root() -> Path:
    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise RuntimeError("A Windows user profile is required.")
    root = Path(profile)
    if not root.is_absolute() or not root.is_dir():
        raise RuntimeError("A Windows user profile is required.")
    return root / "Documents" / "AURORA" / "Projects"


def _ui_root() -> Path:
    return Path(__file__).resolve().parents[2] / "frontend" / "dist"


async def _serve(
    project_root: Path, ui_root: Path, credential_store: WindowsCredentialStore
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((_HOST, 0))
        listener.listen(128)
        port = listener.getsockname()[1]
        origin = f"http://{_HOST}:{port}"
        app = create_desktop_app(
            project_root=project_root,
            credential_store=credential_store,
            allowed_origin=origin,
            ui_root=ui_root,
        )
        config = uvicorn.Config(
            app,
            host=_HOST,
            port=port,
            access_log=False,
            proxy_headers=False,
            server_header=False,
            log_level="warning",
        )
        server = uvicorn.Server(config)
        running = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            while not server.started:
                if running.done():
                    await running
                    raise RuntimeError("The local AURORA server did not start.")
                await asyncio.sleep(0.01)
            _LOGGER.info("AURORA local UI is ready at %s", origin)
            try:
                if not webbrowser.open(origin):
                    _LOGGER.warning("Open the local AURORA UI manually at %s", origin)
            except Exception:
                _LOGGER.warning("Open the local AURORA UI manually at %s", origin)
            await running
        finally:
            server.should_exit = True
            if not running.done():
                await running


def run() -> None:
    """Start AURORA on Windows and block until the local server exits."""
    if sys.platform != "win32":
        _LOGGER.error("The AURORA launcher requires Windows.")
        raise SystemExit(1)
    try:
        project_root = _project_root()
        ui_root = _ui_root()
        validate_bundle(ui_root)
        credential_store = WindowsCredentialStore()
        asyncio.run(_serve(project_root, ui_root, credential_store))
    except KeyboardInterrupt:
        return
    except Exception:
        _LOGGER.error("The local AURORA application could not start.")
        raise SystemExit(1) from None
