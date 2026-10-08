"""Application-owned, loopback-only HTTP translation for approved P1-P3 APIs."""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import asdict, replace
from pathlib import Path
from threading import RLock
from typing import cast
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import JsonValue

from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.generation import (
    GenerationConfigurationError,
    GenerationJob,
    GenerationRequest,
    OpenAIResponsesClient,
)
from src.local_api.schemas import (
    CreateProjectBody,
    CredentialBody,
    SaveProjectBody,
    TextGenerationBody,
)
from src.projects import ProjectDocument, ProjectRepository

_ORIGIN = re.compile(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})\Z")
_MAX_BODY_BYTES = 2 * 1024 * 1024
_SECRET_NAMES = frozenset({"openai_api_key", "netlify_token"})
_MUTATING = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_BODY_METHODS = frozenset({"POST", "PUT", "PATCH"})


def _error(status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": status}})


def _project(document: ProjectDocument) -> dict[str, object]:
    return {"metadata": asdict(document.metadata), "state": document.state}


def _project_id(value: str) -> str:
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=400) from None


def _name(value: str) -> str:
    if not value.strip():
        raise HTTPException(status_code=400)
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise HTTPException(status_code=400) from None
    return value


def _state(value: dict[str, JsonValue]) -> dict[str, JsonValue]:
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
        if _contains_secret(value):
            raise ValueError
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise HTTPException(status_code=400) from None
    return value


def _contains_secret(value: JsonValue) -> bool:
    if isinstance(value, dict):
        return any(
            key.casefold() in _SECRET_NAMES or _contains_secret(item) for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    return False


def _secret_name(value: str) -> SecretName:
    if value not in _SECRET_NAMES:
        raise HTTPException(status_code=400)
    return cast("SecretName", value)


def _job(job: GenerationJob) -> dict[str, object]:
    result = job.result
    failure = job.failure
    return {
        "job_id": job.job_id,
        "status": job.status,
        "result": None
        if result is None
        else {
            "response_id": result.response_id,
            "model": result.model,
            "output_text": result.output_text,
        },
        "failure": None
        if failure is None
        else {
            "category": failure.category,
            "message": failure.message,
            "retryable": failure.retryable,
        },
    }


def create_app(
    *,
    project_root: Path,
    credential_store: WindowsCredentialStore,
    allowed_origin: str,
) -> FastAPI:
    """Build an inert API object for one exact loopback origin."""
    match = _ORIGIN.fullmatch(allowed_origin)
    if match is None or int(match.group(1)) > 65535:
        raise ValueError("A canonical loopback origin is required.")
    parts = urlsplit(allowed_origin)
    expected_host = parts.netloc
    project_lock = RLock()
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    async def local_request_gate(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.headers.get("host") != expected_host:
            return _error(400)
        if request.method in _MUTATING:
            if (
                request.headers.get("origin") != allowed_origin
                or request.headers.get("x-aurora-request") != "1"
            ):
                return _error(400)
            if request.method in _BODY_METHODS:
                media_type = request.headers.get("content-type", "").split(";", 1)[0].strip()
                if media_type.lower() != "application/json":
                    return _error(400)
                length = request.headers.get("content-length")
                if length is not None:
                    try:
                        if int(length) > _MAX_BODY_BYTES:
                            return _error(400)
                    except ValueError:
                        return _error(400)
                body = await request.body()
                if len(body) > _MAX_BODY_BYTES:
                    return _error(400)
        response = await call_next(request)
        return _error(response.status_code) if response.status_code >= 400 else response

    async def validation_error(_request: Request, _error: Exception) -> JSONResponse:
        return _error_response(400)

    async def http_error(_request: Request, error: Exception) -> JSONResponse:
        return _error_response(error.status_code if isinstance(error, HTTPException) else 500)

    async def credential_error(_request: Request, _error: Exception) -> JSONResponse:
        return _error_response(503)

    async def unexpected_error(_request: Request, _error: Exception) -> JSONResponse:
        return _error_response(500)

    app.middleware("http")(local_request_gate)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(CredentialStoreError, credential_error)
    app.add_exception_handler(Exception, unexpected_error)

    def health() -> dict[str, str]:
        return {"status": "ok"}

    def list_projects() -> list[dict[str, object]]:
        with project_lock:
            return [asdict(item) for item in ProjectRepository(project_root).list()]

    def create_project(body: CreateProjectBody) -> dict[str, object]:
        with project_lock:
            return _project(ProjectRepository(project_root).create(_name(body.name)))

    def load_project(project_id: str) -> dict[str, object]:
        with project_lock:
            try:
                return _project(ProjectRepository(project_root).load(_project_id(project_id)))
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None

    def save_project(project_id: str, body: SaveProjectBody) -> dict[str, object]:
        identifier = _project_id(project_id)
        name = _name(body.name)
        state = _state(body.state)
        with project_lock:
            repository = ProjectRepository(project_root)
            try:
                current = repository.load(identifier)
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            if current.metadata.updated_at != body.expected_updated_at:
                raise HTTPException(status_code=409)
            metadata = replace(current.metadata, name=name)
            return _project(repository.save(ProjectDocument(metadata=metadata, state=state)))

    def delete_project(project_id: str) -> Response:
        with project_lock:
            try:
                ProjectRepository(project_root).delete(_project_id(project_id))
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
        return Response(status_code=204)

    def credential_status(name: str) -> dict[str, bool]:
        return {"configured": credential_store.get_secret(_secret_name(name)) is not None}

    def put_credential(name: str, body: CredentialBody) -> Response:
        credential_store.set_secret(_secret_name(name), body.secret.get_secret_value())
        return Response(status_code=204)

    def delete_credential(name: str) -> Response:
        credential_store.delete_secret(_secret_name(name))
        return Response(status_code=204)

    def generate_text(body: TextGenerationBody) -> dict[str, object]:
        key = credential_store.get_secret("openai_api_key")
        if key is None:
            raise HTTPException(status_code=409)
        try:
            client = OpenAIResponsesClient(key)
            job = client.generate(
                GenerationRequest(
                    model=body.model,
                    prompt=body.prompt,
                    instructions=body.instructions,
                )
            )
        except GenerationConfigurationError:
            raise HTTPException(status_code=400) from None
        return _job(job)

    app.add_api_route("/api/v1/health", health, methods=["GET"])
    app.add_api_route("/api/v1/projects", list_projects, methods=["GET"])
    app.add_api_route("/api/v1/projects", create_project, methods=["POST"], status_code=201)
    app.add_api_route("/api/v1/projects/{project_id}", load_project, methods=["GET"])
    app.add_api_route("/api/v1/projects/{project_id}", save_project, methods=["PUT"])
    app.add_api_route(
        "/api/v1/projects/{project_id}", delete_project, methods=["DELETE"], status_code=204
    )
    app.add_api_route("/api/v1/credentials/{name}/status", credential_status, methods=["GET"])
    app.add_api_route(
        "/api/v1/credentials/{name}", put_credential, methods=["PUT"], status_code=204
    )
    app.add_api_route(
        "/api/v1/credentials/{name}", delete_credential, methods=["DELETE"], status_code=204
    )
    app.add_api_route("/api/v1/generation/text", generate_text, methods=["POST"])
    return app


def _error_response(status: int) -> JSONResponse:
    return _error(status)
