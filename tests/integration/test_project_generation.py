"""PG-001 fake P3 through real P7 and P4 without disk or network."""

from __future__ import annotations

import json
from pathlib import Path

from src.editor import load_editor_state, save_editor_state, to_static_site_document
from src.generation import GenerationJob, GenerationRequest, GenerationResult, OpenAIResponsesClient
from src.project_generation import ProjectDraftGenerator, ProjectDraftRequest
from src.site_export import StaticSiteBuilder


class _SyntheticClient(OpenAIResponsesClient):
    def __init__(self) -> None:
        super().__init__("synthetic-test-key")
        self.calls = 0

    def generate(self, request: GenerationRequest) -> GenerationJob:
        self.calls += 1
        return GenerationJob(
            job_id="synthetic-job",
            request=request,
            status="completed",
            result=GenerationResult(
                response_id="synthetic-response",
                model=request.model,
                output_text=json.dumps(
                    {
                        "brand": {
                            "name": "Студия",
                            "tagline": "Для вас",
                            "primary_color": "#123456",
                            "secondary_color": "#abcdef",
                            "font_family": "system",
                        },
                        "pages": [
                            {
                                "slug": "index",
                                "title": "Главная",
                                "meta_description": "Дизайн-студия",
                                "heading": "Добро пожаловать",
                                "sections": [{"heading": "Услуги", "body": "Наши работы"}],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
            ),
        )


def test_candidate_round_trips_through_public_editor_and_build_without_io(tmp_path: Path) -> None:
    client = _SyntheticClient()
    outcome = ProjectDraftGenerator(client).generate(
        ProjectDraftRequest(
            project_name="Студия",
            business_prompt="Создай сайт студии",
            language="ru",
            model="configured-model",
        )
    )
    assert client.calls == 1
    assert outcome.status == "completed"
    assert outcome.document is not None
    saved = save_editor_state({"other": {"kept": True}}, outcome.document)
    assert saved["other"] == {"kept": True}
    loaded = load_editor_state(saved)
    assert loaded == outcome.document
    assert loaded is not None
    build = StaticSiteBuilder().build(to_static_site_document(loaded, ()))
    assert [file.path for file in build.files] == ["assets/site.css", "index.html"]
    html = next(file.data for file in build.files if file.path == "index.html")
    assert "Наши работы".encode() in html
    assert list(tmp_path.iterdir()) == []
