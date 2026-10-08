"""P5-001 fake-HTTP Netlify behavior, failure and safety tests."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest

import src.deployment.netlify as netlify
from src.deployment import NetlifyDeployer, NetlifyDeployError
from src.site_export import SiteExportError, StaticSiteBuild, StaticSiteFile

_SITE_ID = "00000000-0000-0000-0000-000000000001"
_DEPLOY_ID = "deploy-1"
_TOKEN = "fake-token-private"


@dataclass(frozen=True)
class _Call:
    host: str
    timeout: int
    method: str
    path: str
    body: bytes | None
    headers: dict[str, str]


class _Response:
    def __init__(self, data: bytes, status: int = 200) -> None:
        self.status = status
        self._data = data

    def read(self, size: int) -> bytes:
        return self._data[:size]


class _Connection:
    def __init__(
        self,
        host: str,
        timeout: int,
        replies: list[_Response | Exception],
        calls: list[_Call],
    ) -> None:
        self._host = host
        self._timeout = timeout
        self._replies = replies
        self._calls = calls
        self._response: _Response | None = None
        self.closed = False

    def request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._calls.append(_Call(self._host, self._timeout, method, path, body, headers or {}))
        reply = self._replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        self._response = reply

    def getresponse(self) -> _Response:
        assert self._response is not None
        return self._response

    def close(self) -> None:
        self.closed = True


def _reply(value: object, status: int = 200) -> _Response:
    return _Response(json.dumps(value).encode("utf-8"), status)


def _build() -> StaticSiteBuild:
    return StaticSiteBuild(
        files=(
            StaticSiteFile(path="index.html", data=b"<!doctype html><h1>ok</h1>"),
            StaticSiteFile(path="assets/site.css", data=b"body{color:black}"),
        )
    )


def _install(
    monkeypatch: pytest.MonkeyPatch, replies: Sequence[_Response | Exception]
) -> tuple[list[_Call], list[_Connection]]:
    calls: list[_Call] = []
    connections: list[_Connection] = []
    queue = list(replies)

    def factory(host: str, *, timeout: int) -> _Connection:
        connection = _Connection(host, timeout, queue, calls)
        connections.append(connection)
        return connection

    monkeypatch.setattr(netlify, "HTTPSConnection", factory)

    def no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(netlify, "sleep", no_sleep)
    return calls, connections


def _ready(url: str = "https://example.netlify.app") -> _Response:
    return _reply({"id": _DEPLOY_ID, "state": "ready", "ssl_url": url})


def test_new_site_deploys_exact_p4_zip_and_polls_ready(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def temporary_directory(*, prefix: str) -> TemporaryDirectory[str]:
        return TemporaryDirectory(prefix=prefix, dir=tmp_path)

    monkeypatch.setattr(netlify, "TemporaryDirectory", temporary_directory)
    replies = [
        _reply({"id": _SITE_ID}, 201),
        _reply({"id": _DEPLOY_ID}, 201),
        _reply({"id": _DEPLOY_ID, "state": "processing"}),
        _ready(),
    ]
    calls, connections = _install(monkeypatch, replies)

    result = NetlifyDeployer(_TOKEN).deploy(_build())

    assert (result.site_id, result.deploy_id, result.public_url) == (
        _SITE_ID,
        _DEPLOY_ID,
        "https://example.netlify.app",
    )
    assert [call.method for call in calls] == ["POST", "POST", "GET", "GET"]
    assert [call.path for call in calls] == [
        "/api/v1/sites",
        f"/api/v1/sites/{_SITE_ID}/deploys",
        f"/api/v1/deploys/{_DEPLOY_ID}",
        f"/api/v1/deploys/{_DEPLOY_ID}",
    ]
    assert calls[0].body == b"{}"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[1].headers["Content-Type"] == "application/zip"
    assert all(call.host == "api.netlify.com" and call.timeout == 30 for call in calls)
    assert all(call.headers["Authorization"] == f"Bearer {_TOKEN}" for call in calls)
    archive_bytes = calls[1].body
    assert archive_bytes is not None
    with ZipFile(BytesIO(archive_bytes)) as archive:
        assert archive.namelist() == ["assets/site.css", "index.html"]
        assert archive.read("index.html") == b"<!doctype html><h1>ok</h1>"
        assert archive.read("assets/site.css") == b"body{color:black}"
    assert all(connection.closed for connection in connections)
    assert list(tmp_path.iterdir()) == []


def test_existing_site_skips_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), _ready()])
    result = NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert result.site_id == _SITE_ID
    assert [call.method for call in calls] == ["POST", "GET"]
    assert calls[0].path == f"/api/v1/sites/{_SITE_ID}/deploys"


@pytest.mark.parametrize("token", ["", "bad token", "bad\nheader", "é", "\x00"])
def test_invalid_token_has_no_side_effect(token: str, monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(token)
    assert (raised.value.stage, raised.value.category) == ("validation", "invalid_input")
    assert calls == []


@pytest.mark.parametrize(
    "site_id", ["", "example.netlify.app", "../sites", "00000000-0000-0000-0000-00000000000A"]
)
def test_invalid_site_id_rejected_before_network(
    site_id: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(monkeypatch, [])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=site_id)
    assert (raised.value.stage, raised.value.category) == ("validation", "invalid_input")
    assert calls == []


def test_invalid_build_rejected_before_site_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [])
    invalid = StaticSiteBuild(files=(StaticSiteFile(path="bad.txt", data=b"secret"),))
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(invalid)
    assert (raised.value.stage, raised.value.category) == ("validation", "invalid_input")
    assert calls == []
    assert "secret" not in str(raised.value)


def test_export_failure_is_safe_and_precedes_network(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [])

    class FailingExporter:
        def export_zip(self, _build: StaticSiteBuild, _destination: Path) -> Path:
            raise SiteExportError("private local path")

    monkeypatch.setattr(netlify, "StaticSiteExporter", FailingExporter)
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("validation", "invalid_input")
    assert raised.value.__cause__ is None
    assert "private local path" not in str(raised.value)
    assert calls == []


@pytest.mark.parametrize(
    ("status", "category"),
    [(302, "protocol"), (401, "auth"), (403, "auth"), (429, "rate_limit"), (500, "remote")],
)
def test_create_http_failure_never_retries(
    status: int, category: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(monkeypatch, [_reply({"message": "private"}, status)])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("site_create", category)
    assert raised.value.site_id is None
    assert len(calls) == 1
    assert "private" not in str(raised.value)


@pytest.mark.parametrize(
    ("failure", "category"),
    [(TimeoutError("token-containing timeout"), "timeout"), (OSError("token"), "transport")],
)
def test_uncertain_upload_retains_site_without_retry(
    failure: Exception, category: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(monkeypatch, [_reply({"id": _SITE_ID}), failure])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("upload", category)
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, None)
    assert len(calls) == 2
    assert raised.value.__cause__ is None
    assert "token" not in str(raised.value)


@pytest.mark.parametrize(
    ("status", "category"),
    [(302, "protocol"), (401, "auth"), (429, "rate_limit"), (503, "remote")],
)
def test_upload_http_failure_preserves_created_site(
    status: int, category: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(monkeypatch, [_reply({"id": _SITE_ID}), _reply({}, status)])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("upload", category)
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, None)
    assert len(calls) == 2


@pytest.mark.parametrize(
    "response",
    [
        _Response(b"not json"),
        _Response(b"[]"),
        _Response(b"{" + b"x" * (1024 * 1024) + b"}"),
        _reply({"id": "not a uuid"}),
    ],
)
def test_malformed_create_response_is_protocol(
    response: _Response, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(monkeypatch, [response])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("site_create", "protocol")
    assert len(calls) == 1


def test_malformed_upload_response_has_recoverable_site_id(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [_reply({"id": _SITE_ID}), _reply({"id": "a/b"})])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build())
    assert (raised.value.stage, raised.value.category) == ("upload", "protocol")
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, None)
    assert len(calls) == 2


@pytest.mark.parametrize("state", ["error", "failed", "canceled"])
def test_terminal_poll_failure_preserves_both_ids(
    state: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _install(
        monkeypatch, [_reply({"id": _DEPLOY_ID}), _reply({"id": _DEPLOY_ID, "state": state})]
    )
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "failed")
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, _DEPLOY_ID)
    assert len(calls) == 2


@pytest.mark.parametrize(
    "url",
    [
        "http://example.netlify.app",
        "https://user:pass@example.netlify.app",
        "https://",
        " https://example.netlify.app",
    ],
)
def test_invalid_ready_url_is_protocol(url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), _ready(url)])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "protocol")
    assert raised.value.deploy_id == _DEPLOY_ID


def test_poll_wrong_id_is_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), _reply({"id": "wrong", "state": "ready"})])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "protocol")


def test_poll_auth_error_preserves_both_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _ = _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), _reply({}, 401)])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "auth")
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, _DEPLOY_ID)
    assert len(calls) == 2


@pytest.mark.parametrize(
    "response",
    [
        _Response(b"invalid"),
        _Response(b"[1]"),
        _Response(b"{" + b"x" * (1024 * 1024) + b"}"),
        _reply({"id": _DEPLOY_ID, "state": "ready"}),
    ],
)
def test_poll_malformed_response_is_safe_protocol(
    response: _Response, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), response])
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "protocol")
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, _DEPLOY_ID)


def test_poll_deadline_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    pending = _reply({"id": _DEPLOY_ID, "state": "processing"})
    calls, _ = _install(monkeypatch, [_reply({"id": _DEPLOY_ID}), *([pending] * 61)])
    clock = [0.0]

    def fake_time() -> float:
        return clock[0]

    def fake_sleep(seconds: float) -> None:
        clock[0] += seconds

    monkeypatch.setattr(netlify, "monotonic", fake_time)
    monkeypatch.setattr(netlify, "sleep", fake_sleep)
    with pytest.raises(NetlifyDeployError) as raised:
        NetlifyDeployer(_TOKEN).deploy(_build(), site_id=_SITE_ID)
    assert (raised.value.stage, raised.value.category) == ("poll", "timeout")
    assert (raised.value.site_id, raised.value.deploy_id) == (_SITE_ID, _DEPLOY_ID)
    assert clock[0] == 120.0
    assert len(calls) == 61


def test_construction_never_opens_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("constructor opened network")

    monkeypatch.setattr(netlify, "HTTPSConnection", forbidden)
    client = NetlifyDeployer(_TOKEN)
    assert _TOKEN not in repr(client)
