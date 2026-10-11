"""Exact public snapshots, gateway and terminal-invariant acceptance."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass
from inspect import signature
from pathlib import Path
from typing import Literal, get_type_hints

import pytest

import src.project_generation as gateway
from src.editor import EditorDocument
from src.generation import GenerationFailure, OpenAIResponsesClient
from src.project_generation import ProjectDraftGenerator, ProjectDraftOutcome, ProjectDraftRequest


def test_gateway_and_signatures_are_exact() -> None:
    assert set(gateway.__all__) == {
        "ProjectDraftRequest",
        "ProjectDraftOutcome",
        "ProjectDraftGenerator",
    }
    assert get_type_hints(ProjectDraftGenerator.__init__) == {
        "text_client": OpenAIResponsesClient,
        "return": type(None),
    }
    assert get_type_hints(ProjectDraftGenerator.generate) == {
        "request": ProjectDraftRequest,
        "return": ProjectDraftOutcome,
    }
    assert str(signature(ProjectDraftGenerator.generate)) == (
        "(self, request: 'ProjectDraftRequest') -> 'ProjectDraftOutcome'"
    )


def test_exact_immutable_keyword_only_models_and_safe_representations() -> None:
    assert is_dataclass(ProjectDraftRequest)
    assert is_dataclass(ProjectDraftOutcome)
    assert get_type_hints(ProjectDraftRequest) == {
        "project_name": str,
        "business_prompt": str,
        "language": Literal["ru", "en"],
        "model": str,
    }
    assert get_type_hints(ProjectDraftOutcome) == {
        "job_id": str,
        "status": Literal["completed", "failed"],
        "document": EditorDocument | None,
        "failure": GenerationFailure | None,
    }
    assert [field.name for field in fields(ProjectDraftRequest)] == [
        "project_name",
        "business_prompt",
        "language",
        "model",
    ]
    assert [field.name for field in fields(ProjectDraftOutcome)] == [
        "job_id",
        "status",
        "document",
        "failure",
    ]
    assert all(field.kw_only for field in fields(ProjectDraftRequest))
    assert all(field.kw_only for field in fields(ProjectDraftOutcome))
    request = ProjectDraftRequest(
        project_name="Studio", business_prompt="private-business-text", language="en", model="m"
    )
    assert not hasattr(request, "__dict__")
    assert "private-business-text" not in repr(request)
    with pytest.raises(FrozenInstanceError):
        request.project_name = "Other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        ProjectDraftRequest("Studio", "text", "en", "m")  # type: ignore[misc]


def test_terminal_outcome_invariants() -> None:
    failure = GenerationFailure(category="network", message="Safe failure.", retryable=True)
    outcome = ProjectDraftOutcome(job_id="j", status="failed", failure=failure)
    assert outcome.failure == failure
    assert not hasattr(outcome, "__dict__")
    with pytest.raises(FrozenInstanceError):
        outcome.status = "completed"  # type: ignore[misc]
    for status, value in (("completed", None), ("failed", None)):
        with pytest.raises(ValueError, match="matching terminal result"):
            ProjectDraftOutcome(job_id="j", status=status, document=value)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="matching terminal result"):
        ProjectDraftOutcome(job_id="j", status="completed", failure=failure)


def test_exact_module_files_and_public_application_imports_only() -> None:
    root = Path(__file__).parents[2]
    package = root / "src" / "project_generation"
    assert {path.name for path in package.glob("*.py")} == {
        "__init__.py",
        "models.py",
        "service.py",
    }
    allowed: dict[str, set[str]] = {
        "__init__.py": {"src.project_generation.models", "src.project_generation.service"},
        "models.py": set(),
        "service.py": {
            "src.editor",
            "src.generation",
            "src.project_generation.models",
            "src.site_export",
        },
    }
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.level == 0
                if node.module is not None and node.module.startswith("src."):
                    assert node.module in allowed[path.name]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "print"
    for path in (root / "src").rglob("*.py"):
        if package not in path.parents:
            assert "src.project_generation" not in path.read_text(encoding="utf-8")
