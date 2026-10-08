"""Public gateway for the P6 local application API foundation."""

from src.local_api.app import create_app

__all__ = ["create_app"]
