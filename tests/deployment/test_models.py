"""P5-001 public model and error contract assertions."""

from dataclasses import FrozenInstanceError, fields

import pytest

import src.deployment as deployment
from src.deployment.models import NetlifyDeployError, NetlifyDeployment


def test_public_gateway_is_exact() -> None:
    assert deployment.__all__ == [
        "NetlifyDeployError",
        "NetlifyDeployer",
        "NetlifyDeployment",
    ]
    assert deployment.NetlifyDeployment is NetlifyDeployment
    assert deployment.NetlifyDeployError is NetlifyDeployError


def test_deployment_is_frozen_slotted_and_keyword_only() -> None:
    result = NetlifyDeployment(
        site_id="site", deploy_id="deploy", public_url="https://example.netlify.app"
    )
    assert [field.name for field in fields(result)] == ["site_id", "deploy_id", "public_url"]
    assert result.__slots__ == ("site_id", "deploy_id", "public_url")
    with pytest.raises(FrozenInstanceError):
        result.site_id = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        NetlifyDeployment("site", "deploy", "https://example.netlify.app")  # type: ignore[misc]


def test_error_has_safe_read_only_fields() -> None:
    error = NetlifyDeployError("upload", "transport", "site", None)
    assert isinstance(error, RuntimeError)
    assert error.stage == "upload"
    assert error.category == "transport"
    assert error.site_id == "site"
    assert error.deploy_id is None
    assert str(error) == "Netlify deployment upload: transport."
    assert repr(error) == "NetlifyDeployError('Netlify deployment upload: transport.')"
    with pytest.raises(AttributeError):
        error.stage = "poll"  # type: ignore[misc]
