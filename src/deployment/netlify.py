"""AURORA P5-001 explicit, bounded Netlify ZIP deployment adapter."""

from __future__ import annotations

import json
import re
from contextlib import suppress
from http.client import HTTPException, HTTPSConnection
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from typing import Literal, cast
from urllib.parse import urlsplit

from src.deployment.models import NetlifyDeployError, NetlifyDeployment
from src.site_export import (
    SiteExportError,
    SiteValidationError,
    StaticSiteBuild,
    StaticSiteExporter,
)

type _Stage = Literal["validation", "site_create", "upload", "poll"]

_API_HOST = "api.netlify.com"
_API_PATH = "/api/v1"
_SITE_ID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")
_DEPLOY_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
_MAX_RESPONSE_BYTES = 1024 * 1024
_REQUEST_TIMEOUT_SECONDS = 30
_POLL_DEADLINE_SECONDS = 120
_POLL_INTERVAL_SECONDS = 2


class NetlifyDeployer:
    """Deploy one trusted P4 build only when its caller explicitly invokes deploy."""

    __slots__ = ("_api_token",)

    def __init__(self, api_token: str) -> None:
        if (
            type(api_token) is not str
            or not api_token
            or any(ord(char) < 33 or ord(char) > 126 for char in api_token)
        ):
            raise NetlifyDeployError("validation", "invalid_input")
        self._api_token = api_token

    def deploy(self, build: StaticSiteBuild, *, site_id: str | None = None) -> NetlifyDeployment:
        """Stage a deterministic ZIP, then create/reuse a site and poll once deployed."""
        if site_id is not None and not _valid_site_id(site_id):
            raise NetlifyDeployError("validation", "invalid_input")

        try:
            with TemporaryDirectory(prefix="aurora-netlify-") as directory:
                zip_path = StaticSiteExporter().export_zip(build, Path(directory) / "site.zip")
                archive = zip_path.read_bytes()
        except (SiteValidationError, SiteExportError, OSError):
            raise NetlifyDeployError("validation", "invalid_input") from None

        if site_id is None:
            site_response = self._request_json(
                "POST", "/sites", b"{}", "application/json", "site_create", None, None
            )
            site_id = _site_id(site_response.get("id"), "site_create")

        deploy_response = self._request_json(
            "POST",
            f"/sites/{site_id}/deploys",
            archive,
            "application/zip",
            "upload",
            site_id,
            None,
        )
        deploy_id = _deploy_id(deploy_response.get("id"), site_id)
        return self._poll(site_id, deploy_id)

    def _poll(self, site_id: str, deploy_id: str) -> NetlifyDeployment:
        deadline = monotonic() + _POLL_DEADLINE_SECONDS
        while True:
            if monotonic() >= deadline:
                raise NetlifyDeployError("poll", "timeout", site_id, deploy_id)
            response = self._request_json(
                "GET", f"/deploys/{deploy_id}", None, None, "poll", site_id, deploy_id
            )
            if monotonic() >= deadline:
                raise NetlifyDeployError("poll", "timeout", site_id, deploy_id)
            if response.get("id") != deploy_id or type(response.get("state")) is not str:
                raise NetlifyDeployError("poll", "protocol", site_id, deploy_id)
            state = response["state"]
            if state == "ready":
                public_url = _public_url(response.get("ssl_url"), site_id, deploy_id)
                return NetlifyDeployment(
                    site_id=site_id, deploy_id=deploy_id, public_url=public_url
                )
            if state in ("error", "failed", "canceled"):
                raise NetlifyDeployError("poll", "failed", site_id, deploy_id)
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise NetlifyDeployError("poll", "timeout", site_id, deploy_id)
            sleep(min(_POLL_INTERVAL_SECONDS, remaining))

    def _request_json(
        self,
        method: Literal["GET", "POST"],
        path: str,
        body: bytes | None,
        content_type: str | None,
        stage: Literal["site_create", "upload", "poll"],
        site_id: str | None,
        deploy_id: str | None,
    ) -> dict[str, object]:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Accept": "application/json",
        }
        if content_type is not None:
            headers["Content-Type"] = content_type
        try:
            connection = HTTPSConnection(_API_HOST, timeout=_REQUEST_TIMEOUT_SECONDS)
            try:
                connection.request(method, _API_PATH + path, body=body, headers=headers)
                response = connection.getresponse()
                status = response.status
                if 300 <= status < 400:
                    raise NetlifyDeployError(stage, "protocol", site_id, deploy_id)
                if status in (401, 403):
                    raise NetlifyDeployError(stage, "auth", site_id, deploy_id)
                if status == 429:
                    raise NetlifyDeployError(stage, "rate_limit", site_id, deploy_id)
                if not 200 <= status < 300:
                    raise NetlifyDeployError(stage, "remote", site_id, deploy_id)
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
            finally:
                with suppress(OSError, HTTPException):
                    connection.close()
        except TimeoutError:
            raise NetlifyDeployError(stage, "timeout", site_id, deploy_id) from None
        except (OSError, HTTPException):
            raise NetlifyDeployError(stage, "transport", site_id, deploy_id) from None

        if type(raw) is not bytes or len(raw) > _MAX_RESPONSE_BYTES:
            raise NetlifyDeployError(stage, "protocol", site_id, deploy_id)
        try:
            parsed: object = json.loads(raw)
        except (ValueError, UnicodeError, RecursionError):
            raise NetlifyDeployError(stage, "protocol", site_id, deploy_id) from None
        if type(parsed) is not dict:
            raise NetlifyDeployError(stage, "protocol", site_id, deploy_id)
        record = cast("dict[object, object]", parsed)
        if any(type(key) is not str for key in record):
            raise NetlifyDeployError(stage, "protocol", site_id, deploy_id)
        return cast("dict[str, object]", record)


def _valid_site_id(value: object) -> bool:
    return type(value) is str and _SITE_ID.fullmatch(value) is not None


def _site_id(value: object, stage: _Stage) -> str:
    if not _valid_site_id(value):
        raise NetlifyDeployError(stage, "protocol")
    return cast("str", value)


def _deploy_id(value: object, site_id: str) -> str:
    if type(value) is not str or _DEPLOY_ID.fullmatch(value) is None:
        raise NetlifyDeployError("upload", "protocol", site_id)
    return value


def _public_url(value: object, site_id: str, deploy_id: str) -> str:
    if type(value) is not str or not value or any(ord(char) < 33 for char in value):
        raise NetlifyDeployError("poll", "protocol", site_id, deploy_id)
    try:
        parts = urlsplit(value)
        valid = (
            parts.scheme == "https"
            and bool(parts.hostname)
            and parts.username is None
            and parts.password is None
        )
        _ = parts.port
    except ValueError:
        valid = False
    if not valid:
        raise NetlifyDeployError("poll", "protocol", site_id, deploy_id)
    return value


__all__ = ["NetlifyDeployer"]
