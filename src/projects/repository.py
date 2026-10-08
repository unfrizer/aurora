"""Validated, atomic filesystem persistence for AURORA projects."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import stat
import tempfile
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast
from uuid import UUID, uuid4

from src.core.exceptions import ValidationError
from src.core.types import JSONDict, JSONValue
from src.projects.models import ProjectDocument, ProjectMetadata

_ASSET_REFERENCE = re.compile(r"assets/([0-9a-f]{64})\.(png|jpg|gif|webp)")
_ASSET_NAME = re.compile(r"[0-9a-f]{64}\.(png|jpg|gif|webp)")
_ASSET_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}
_MAX_ASSET_BYTES = 16 * 1024 * 1024
_MAX_ASSET_COUNT = 256
_MAX_TOTAL_ASSET_BYTES = 128 * 1024 * 1024


class ProjectRepository:
    """Own portable project folders under one explicit filesystem root."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def create(self, name: str, state: JSONDict | None = None) -> ProjectDocument:
        self._validate_name(name)
        now = self._now()
        metadata = ProjectMetadata(
            project_id=str(uuid4()),
            name=name.strip(),
            format_version="1.0",
            created_at=now,
            updated_at=now,
        )
        document = self._validated_document(
            ProjectDocument(metadata=metadata, state={} if state is None else state)
        )
        path = self._path_for(metadata)
        path.mkdir(parents=True, exist_ok=False)
        try:
            for directory in ("assets", "site", "exports"):
                (path / directory).mkdir()
            self._write_document(path, document)
        except (OSError, ValidationError):
            # This directory was created exclusively by this call and has not
            # been returned to a caller yet.
            shutil.rmtree(path)
            raise
        return document

    def save(self, document: ProjectDocument) -> ProjectDocument:
        document = self._validated_document(document)
        path = self._existing_path(document.metadata.project_id)
        previous = self._load_path(path)
        if document.metadata.created_at != previous.metadata.created_at:
            raise ValidationError("Project creation time cannot be changed")
        updated = replace(
            document.metadata, name=document.metadata.name.strip(), updated_at=self._now()
        )
        result = self._validated_document(ProjectDocument(metadata=updated, state=document.state))
        self._write_document(path, result, previous=previous)
        return result

    def load(self, project_id: str) -> ProjectDocument:
        return self._load_path(self._existing_path(project_id))

    def list(self) -> tuple[ProjectMetadata, ...]:
        if not self._root.exists():
            return ()
        projects = [
            self._load_path(path).metadata
            for path in self._root.iterdir()
            if (path / "aurora.project.json").exists()
        ]
        ids = [item.project_id for item in projects]
        if len(ids) != len(set(ids)):
            raise ValidationError("Multiple directories have the same project ID")
        return tuple(
            sorted(
                projects,
                key=lambda item: (datetime.fromisoformat(item.updated_at), item.project_id),
                reverse=True,
            )
        )

    def delete(self, project_id: str) -> None:
        path = self._existing_path(project_id)
        self._load_path(path)  # Verify identity and structure before removing a directory.
        shutil.rmtree(path)

    def write_asset(
        self,
        project_id: str,
        data: bytes,
        media_type: Literal["image/png", "image/jpeg", "image/gif", "image/webp"],
    ) -> str:
        """Store validated raster bytes under a deterministic project-local reference."""
        if type(data) is not bytes or not data or len(data) > _MAX_ASSET_BYTES:
            raise _invalid_asset()
        if type(media_type) is not str:
            raise _invalid_asset()
        extension = _ASSET_EXTENSIONS.get(media_type)
        if extension is None or not _has_signature(extension, data):
            raise _invalid_asset()
        reference = f"assets/{hashlib.sha256(data).hexdigest()}.{extension}"
        directory = self._asset_directory(self._existing_path(project_id))
        destination = directory / reference.removeprefix("assets/")
        try:
            existing = _read_managed_asset(destination, reference)
        except FileNotFoundError:
            existing = None
        if existing is not None:
            if existing != data:
                raise _invalid_asset()
            return reference
        count, total = _managed_usage(directory)
        if count >= _MAX_ASSET_COUNT or total + len(data) > _MAX_TOTAL_ASSET_BYTES:
            raise _invalid_asset()
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "wb", dir=directory, prefix=".aurora-asset-", delete=False
            ) as file:
                temporary = Path(file.name)
                file.write(data)
                file.flush()
                os.fsync(file.fileno())
            try:
                os.link(temporary, destination)
            except FileExistsError:
                if _read_managed_asset(destination, reference) != data:
                    raise _invalid_asset() from None
            return reference
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def read_asset(self, project_id: str, path: str) -> bytes:
        """Return detached, integrity-checked raster bytes from this project."""
        _validate_asset_reference(path)
        directory = self._asset_directory(self._existing_path(project_id))
        return _read_managed_asset(directory / path.removeprefix("assets/"), path)

    def delete_asset(self, project_id: str, path: str) -> bool:
        """Remove an unreferenced managed asset without changing project state."""
        _validate_asset_reference(path)
        project = self._existing_path(project_id)
        directory = self._asset_directory(project)
        target = directory / path.removeprefix("assets/")
        try:
            _read_managed_asset(target, path)
        except FileNotFoundError:
            return False
        document = self._load_path(project)
        if _contains_string_value(document.state, path):
            raise _invalid_asset()
        target.unlink()
        return True

    def _asset_directory(self, project: Path) -> Path:
        self._load_path(project)
        directory = project / "assets"
        if (
            directory.is_symlink()
            or directory.is_junction()
            or not directory.is_dir()
            or directory.resolve() != directory
        ):
            raise _invalid_asset()
        return directory

    def _path_for(self, metadata: ProjectMetadata) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", metadata.name.lower()).strip("-")[:80] or "project"
        return self._root / f"{slug}-{metadata.project_id}"

    def _existing_path(self, project_id: str) -> Path:
        project_id = self._validated_id(project_id)
        if not self._root.exists():
            raise FileNotFoundError("Project not found")
        matches = [path for path in self._root.iterdir() if path.name.endswith(f"-{project_id}")]
        if not matches:
            raise FileNotFoundError("Project not found")
        if len(matches) != 1:
            raise ValidationError("Multiple directories have the same project ID")
        self._validate_path(matches[0])
        return matches[0]

    def _validate_path(self, path: Path) -> None:
        if (
            path.parent != self._root
            or path.is_symlink()
            or path.is_junction()
            or path.resolve().parent != self._root
            or not path.is_dir()
        ):
            raise ValidationError("Project must be a direct directory inside the repository")
        for filename in ("aurora.project.json", "state.json"):
            file = path / filename
            if file.is_symlink() or file.is_junction() or file.resolve().parent != path:
                raise ValidationError("Project files must not link outside their directory")

    def _load_path(self, path: Path) -> ProjectDocument:
        self._validate_path(path)
        try:
            metadata_value: object = json.loads(
                (path / "aurora.project.json").read_text(encoding="utf-8")
            )
            state_value: object = json.loads((path / "state.json").read_text(encoding="utf-8"))
        except (UnicodeError, ValueError, RecursionError):
            raise ValidationError("Project files must contain valid UTF-8 JSON") from None
        metadata = self._metadata_from_json(metadata_value)
        if not path.name.endswith(f"-{metadata.project_id}"):
            raise ValidationError("Project directory and metadata identity do not match")
        state = self._copy_state(state_value)
        return ProjectDocument(metadata=metadata, state=state)

    def _write_document(
        self,
        path: Path,
        document: ProjectDocument,
        *,
        previous: ProjectDocument | None = None,
    ) -> None:
        self._validate_path(path)
        # Validate both payloads before replacing either file. State is the
        # canonical content; a process interruption can only leave older metadata.
        metadata = self._serialize(asdict(document.metadata))
        state = self._serialize(document.state)
        self._write_json(path / "state.json", state)
        try:
            self._write_json(path / "aurora.project.json", metadata)
        except OSError:
            if previous is not None:
                self._write_json(path / "state.json", self._serialize(previous.state))
            raise

    @staticmethod
    def _write_json(path: Path, payload: str) -> None:
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent, prefix=".aurora-", delete=False
            ) as file:
                temporary = Path(file.name)
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @staticmethod
    def _serialize(value: object) -> str:
        try:
            payload = json.dumps(
                value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
            )
            payload.encode("utf-8")
            return payload
        except (TypeError, ValueError, UnicodeError, RecursionError):
            raise ValidationError("Project data must be valid JSON-compatible UTF-8") from None

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(cast(object, name), str) or not name.strip():
            raise ValidationError("Project name must be non-empty")

    @staticmethod
    def _validated_id(project_id: str) -> str:
        try:
            return str(UUID(project_id))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError("Project ID must be a UUID string") from None

    def _metadata_from_json(self, value: object) -> ProjectMetadata:
        if not isinstance(value, dict):
            raise ValidationError("Project metadata must be a JSON object")
        values = cast(dict[object, object], value)
        fields = {"project_id", "name", "format_version", "created_at", "updated_at"}
        if set(values) != fields or any(not isinstance(item, str) for item in values.values()):
            raise ValidationError("Project metadata fields must match the supported format")
        strings = cast(dict[str, str], values)
        metadata = ProjectMetadata(**strings)
        self._validate_name(metadata.name)
        if self._validated_id(metadata.project_id) != metadata.project_id:
            raise ValidationError("Project metadata ID must be a canonical UUID string")
        if metadata.format_version != "1.0":
            raise ValidationError("Unsupported project format version")
        try:
            created = datetime.fromisoformat(metadata.created_at)
            updated = datetime.fromisoformat(metadata.updated_at)
            if (
                created.utcoffset() != UTC.utcoffset(None)
                or updated.utcoffset() != UTC.utcoffset(None)
                or created > updated
            ):
                raise ValueError
        except ValueError:
            raise ValidationError(
                "Project timestamps must be ordered UTC ISO-8601 values"
            ) from None
        self._serialize(asdict(metadata))
        return metadata

    def _validated_document(self, document: ProjectDocument) -> ProjectDocument:
        metadata = self._metadata_from_json(asdict(document.metadata))
        state = self._copy_state(document.state)
        return ProjectDocument(metadata=metadata, state=state)

    @staticmethod
    def _copy_state(value: object) -> JSONDict:
        if not isinstance(value, dict):
            raise ValidationError("Project state must be a JSON object")
        try:
            state = _copy_json(cast(object, value), set())
        except RecursionError:
            raise ValidationError("Project state nesting is too deep") from None
        ProjectRepository._serialize(state)
        return cast(JSONDict, state)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()


def _copy_json(value: object, ancestors: set[int]) -> JSONValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, (dict, list)):
        identity = id(cast(object, value))
        if identity in ancestors:
            raise ValidationError("Project state must not contain circular references")
        ancestors.add(identity)
        try:
            if isinstance(value, list):
                return [_copy_json(item, ancestors) for item in cast(list[object], value)]
            result: JSONDict = {}
            for key, item in cast(dict[object, object], value).items():
                if not isinstance(key, str):
                    raise ValidationError("Project state object keys must be strings")
                result[key] = _copy_json(item, ancestors)
            return result
        finally:
            ancestors.remove(identity)
    raise ValidationError("Project state must contain only JSON values and finite numbers")


def _invalid_asset() -> ValidationError:
    return ValidationError("Invalid project asset.")


def _validate_asset_reference(path: object) -> None:
    if type(path) is not str or _ASSET_REFERENCE.fullmatch(path) is None:
        raise _invalid_asset()


def _has_signature(extension: str, data: bytes) -> bool:
    if extension == "png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == "jpg":
        return data.startswith(b"\xff\xd8\xff")
    if extension == "gif":
        return data.startswith((b"GIF87a", b"GIF89a"))
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def _managed_stat(path: Path) -> os.stat_result:
    if path.is_symlink() or path.is_junction():
        raise _invalid_asset()
    try:
        result = path.lstat()
    except FileNotFoundError:
        raise FileNotFoundError("Project asset not found") from None
    if (
        not stat.S_ISREG(result.st_mode)
        or result.st_size < 1
        or result.st_size > _MAX_ASSET_BYTES
        or path.resolve().parent != path.parent
    ):
        raise _invalid_asset()
    return result


def _read_managed_asset(path: Path, reference: str) -> bytes:
    size = _managed_stat(path).st_size
    with path.open("rb") as file:
        data = file.read(_MAX_ASSET_BYTES + 1)
    match = _ASSET_REFERENCE.fullmatch(reference)
    if (
        match is None
        or len(data) != size
        or hashlib.sha256(data).hexdigest() != match.group(1)
        or not _has_signature(match.group(2), data)
    ):
        raise _invalid_asset()
    return data


def _managed_usage(directory: Path) -> tuple[int, int]:
    count = 0
    total = 0
    for entry in directory.iterdir():
        if _ASSET_NAME.fullmatch(entry.name) is None:
            continue
        total += _managed_stat(entry).st_size
        count += 1
        if count > _MAX_ASSET_COUNT or total > _MAX_TOTAL_ASSET_BYTES:
            raise _invalid_asset()
    return count, total


def _contains_string_value(value: JSONValue, target: str) -> bool:
    pending: list[JSONValue] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, str):
            if current == target:
                return True
        elif isinstance(current, dict):
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    return False


__all__ = ["ProjectRepository"]
