"""AURORA P5-001 immutable result and sanitized deployment failure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type _Stage = Literal["validation", "site_create", "upload", "poll"]
type _Category = Literal[
    "invalid_input", "auth", "rate_limit", "remote", "transport", "protocol", "failed", "timeout"
]


@dataclass(frozen=True, slots=True, kw_only=True)
class NetlifyDeployment:
    """A ready deploy's recoverable identifiers and HTTPS site URL."""

    site_id: str
    deploy_id: str
    public_url: str


class NetlifyDeployError(RuntimeError):
    """Safe failure carrying only the stage, category and known identifiers."""

    __slots__ = ("_category", "_deploy_id", "_site_id", "_stage")

    _stage: _Stage
    _category: _Category
    _site_id: str | None
    _deploy_id: str | None

    def __init__(
        self,
        stage: _Stage,
        category: _Category,
        site_id: str | None = None,
        deploy_id: str | None = None,
    ) -> None:
        super().__init__(f"Netlify deployment {stage}: {category}.")
        self._stage = stage
        self._category = category
        self._site_id = site_id
        self._deploy_id = deploy_id

    @property
    def stage(self) -> _Stage:
        return self._stage

    @property
    def category(self) -> _Category:
        return self._category

    @property
    def site_id(self) -> str | None:
        return self._site_id

    @property
    def deploy_id(self) -> str | None:
        return self._deploy_id


__all__ = ["NetlifyDeployError", "NetlifyDeployment"]
