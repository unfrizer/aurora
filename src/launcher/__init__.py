"""Public gateway for the Windows local application launcher."""

from src.launcher.desktop import create_desktop_app
from src.launcher.server import run

__all__ = ["create_desktop_app", "run"]
