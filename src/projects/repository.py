"""Atomic filesystem persistence for AURORA projects."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from src.core.exceptions import ValidationError
from src.core.types import JSONDict
from src.projects.models import ProjectDocument, ProjectMetadata


class ProjectRepository:
    """Own portable project folders under one explicit filesystem root."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def create(self, name: str, state: JSONDict | None = None) -> ProjectDocument:
        self._validate_name(name)
        now = self._now()
        project_id = str(uuid4())
        metadata = ProjectMetadata(
            project_id=project_id,
            name=name.strip(),
            format_version="1.0",
            created_at=now,
            updated_at=now,
        )
        document = ProjectDocument(metadata=metadata, state={} if state is None else state)
        path = self._path_for(metadata)
        path.mkdir(parents=True, exist_ok=False)
        for directory in ("assets", "site", "exports"):
            (path / directory).mkdir()
        self._write_document(path, document)
        return document

    def save(self, document: ProjectDocument) -> ProjectDocument:
        self._validate_document(document)
        updated = replace(document.metadata, updated_at=self._now())
        result = ProjectDocument(metadata=updated, state=document.state)
        self._write_document(self._existing_path(updated.project_id), result)
        return result

    def load(self, project_id: str) -> ProjectDocument:
        path = self._existing_path(project_id)
        metadata = json.loads((path / "aurora.project.json").read_text(encoding="utf-8"))
        state = json.loads((path / "state.json").read_text(encoding="utf-8"))
        return ProjectDocument(metadata=ProjectMetadata(**metadata), state=state)

    def list(self) -> tuple[ProjectMetadata, ...]:
        if not self._root.exists():
            return ()
        return tuple(
            sorted(
                (
                    self.load(path.name.rsplit("-", 1)[-1]).metadata
                    for path in self._root.iterdir()
                    if (path / "aurora.project.json").is_file()
                ),
                key=lambda item: item.updated_at,
                reverse=True,
            )
        )

    def delete(self, project_id: str) -> None:
        shutil.rmtree(self._existing_path(project_id))

    def _path_for(self, metadata: ProjectMetadata) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", metadata.name.lower()).strip("-") or "project"
        return self._root / f"{slug}-{metadata.project_id}"

    def _existing_path(self, project_id: str) -> Path:
        matches = tuple(self._root.glob(f"*-{project_id}"))
        if len(matches) != 1:
            raise FileNotFoundError(f"Project not found: {project_id}")
        return matches[0]

    def _write_document(self, path: Path, document: ProjectDocument) -> None:
        self._write_json(
            path / "aurora.project.json",
            document.metadata.__dict__
            if False
            else {
                "project_id": document.metadata.project_id,
                "name": document.metadata.name,
                "format_version": document.metadata.format_version,
                "created_at": document.metadata.created_at,
                "updated_at": document.metadata.updated_at,
            },
        )
        self._write_json(path / "state.json", document.state)

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        try:
            payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
        except TypeError as error:
            raise ValidationError("Project state must be JSON-compatible") from error
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as file:
            file.write(payload)
            temporary = Path(file.name)
        temporary.replace(path)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name.strip():
            raise ValidationError("Project name must be non-empty")

    def _validate_document(self, document: ProjectDocument) -> None:
        self._validate_name(document.metadata.name)
        try:
            json.dumps(document.state)
        except TypeError as error:
            raise ValidationError("Project state must be JSON-compatible") from error

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()


__all__ = ["ProjectRepository"]
