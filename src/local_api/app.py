"""Application-owned, loopback-only HTTP translation for approved product APIs."""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import asdict, replace
from pathlib import Path
from threading import RLock
from typing import Literal, cast
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import JsonValue

from src.core.exceptions import ValidationError
from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.editor import (
    EditorStateError,
    load_editor_state,
    save_editor_state,
    to_static_site_document,
)
from src.generation import (
    GenerationConfigurationError,
    GenerationJob,
    GenerationRequest,
    OpenAIResponsesClient,
)
from src.local_api.schemas import (
    CreateProjectBody,
    CredentialBody,
    SaveEditorBody,
    SaveProjectBody,
    TextGenerationBody,
)
from src.projects import ProjectDocument, ProjectRepository
from src.site_export import SiteValidationError, StaticSiteAsset, StaticSiteBuilder

_ORIGIN = re.compile(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})\Z")
_MAX_BODY_BYTES = 2 * 1024 * 1024
_MAX_ASSET_BODY_BYTES = 16 * 1024 * 1024
_ASSET_UPLOAD = re.compile(r"/api/v1/projects/[^/]+/assets\Z")
_ASSET_MEDIA: dict[str, str] = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
}
_PREVIEW_CSP = (
    "default-src 'none'; style-src 'self'; img-src 'self'; "
    "script-src 'none'; connect-src 'none'; form-action 'none'; "
    "base-uri 'none'; frame-ancestors 'self'"
)
type _RasterMediaType = Literal["image/png", "image/jpeg", "image/gif", "image/webp"]
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
                if request.method == "POST" and _ASSET_UPLOAD.fullmatch(request.url.path):
                    media_type = request.headers.get("content-type")
                    if media_type not in _ASSET_MEDIA.values():
                        return _error(400)
                    length = request.headers.get("content-length")
                    if length is not None and (
                        not length.isdecimal() or int(length) > _MAX_ASSET_BODY_BYTES
                    ):
                        return _error(400)
                    body = bytearray()
                    async for chunk in request.stream():
                        if len(chunk) > _MAX_ASSET_BODY_BYTES - len(body):
                            return _error(400)
                        body.extend(chunk)
                    request.state.asset_data = bytes(body)
                    del body
                else:
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
                    body_json = await request.body()
                    if len(body_json) > _MAX_BODY_BYTES:
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

    def save_editor(project_id: str, body: SaveEditorBody) -> dict[str, object]:
        identifier = _project_id(project_id)
        with project_lock:
            repository = ProjectRepository(project_root)
            try:
                current = repository.load(identifier)
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            if current.metadata.updated_at != body.expected_updated_at:
                raise HTTPException(status_code=409)
            try:
                editor = load_editor_state({"editor": body.editor})
                if editor is None:
                    raise HTTPException(status_code=400)
                state = save_editor_state(current.state, editor)
                _state(state)
                return _project(
                    repository.save(ProjectDocument(metadata=current.metadata, state=state))
                )
            except (EditorStateError, ValidationError):
                raise HTTPException(status_code=400) from None

    async def upload_asset(project_id: str, request: Request) -> dict[str, str]:
        identifier = _project_id(project_id)
        data = cast(bytes, request.state.asset_data)
        media_type = cast(_RasterMediaType, request.headers["content-type"])
        with project_lock:
            try:
                path = ProjectRepository(project_root).write_asset(identifier, data, media_type)
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            except ValidationError:
                raise HTTPException(status_code=400) from None
        return {"path": path}

    def read_asset(project_id: str, asset_name: str) -> Response:
        identifier = _project_id(project_id)
        with project_lock:
            try:
                data = ProjectRepository(project_root).read_asset(
                    identifier, f"assets/{asset_name}"
                )
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            except ValidationError:
                raise HTTPException(status_code=400) from None
        media_type = _ASSET_MEDIA[asset_name.rsplit(".", 1)[-1]]
        return Response(
            content=data,
            media_type=media_type,
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Cross-Origin-Resource-Policy": "same-origin",
            },
        )

    def preview_site(project_id: str, file_path: str) -> Response:
        identifier = _project_id(project_id)
        with project_lock:
            repository = ProjectRepository(project_root)
            try:
                current = repository.load(identifier)
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            try:
                editor = load_editor_state(current.state)
                if editor is None:
                    raise HTTPException(status_code=400)
                references: list[str] = []
                seen: set[str] = set()
                if editor.brand.logo_path is not None:
                    references.append(editor.brand.logo_path)
                    seen.add(editor.brand.logo_path)
                for page in editor.pages:
                    for section in page.sections:
                        reference = section.image_path
                        if reference is not None and reference not in seen:
                            references.append(reference)
                            seen.add(reference)
                assets = tuple(
                    StaticSiteAsset(
                        path=reference,
                        data=repository.read_asset(identifier, reference),
                    )
                    for reference in references
                )
                document = to_static_site_document(editor, assets)
                build = StaticSiteBuilder().build(document)
            except (EditorStateError, SiteValidationError, ValidationError, FileNotFoundError):
                raise HTTPException(status_code=400) from None

        for site_file in build.files:
            if site_file.path != file_path:
                continue
            headers = {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Cross-Origin-Resource-Policy": "same-origin",
            }
            if site_file.path.endswith(".html"):
                headers["Content-Security-Policy"] = _PREVIEW_CSP
                media_type = "text/html"
            elif site_file.path == "assets/site.css":
                media_type = "text/css"
            else:
                media_type = _ASSET_MEDIA[site_file.path.rsplit(".", 1)[-1]]
            return Response(content=site_file.data, media_type=media_type, headers=headers)
        raise HTTPException(status_code=404)

    def delete_asset(project_id: str, asset_name: str) -> Response:
        identifier = _project_id(project_id)
        with project_lock:
            try:
                removed = ProjectRepository(project_root).delete_asset(
                    identifier, f"assets/{asset_name}"
                )
            except FileNotFoundError:
                raise HTTPException(status_code=404) from None
            except ValidationError:
                raise HTTPException(status_code=400) from None
        if not removed:
            raise HTTPException(status_code=404)
        return Response(status_code=204)

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
    app.add_api_route("/api/v1/projects/{project_id}/editor", save_editor, methods=["PUT"])
    app.add_api_route(
        "/api/v1/projects/{project_id}/assets", upload_asset, methods=["POST"], status_code=201
    )
    app.add_api_route(
        "/api/v1/projects/{project_id}/assets/{asset_name}", read_asset, methods=["GET"]
    )
    app.add_api_route(
        "/api/v1/projects/{project_id}/preview/{file_path:path}", preview_site, methods=["GET"]
    )
    app.add_api_route(
        "/api/v1/projects/{project_id}/assets/{asset_name}",
        delete_asset,
        methods=["DELETE"],
        status_code=204,
    )
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
