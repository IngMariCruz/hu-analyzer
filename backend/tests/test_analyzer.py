"""
Pruebas del orquestador `analyze` con un proveedor LLM falso (sin red).
"""

import asyncio

import pytest

from app.services.analyzer import analyze
from app.services.file_parser import ParsedHU
from app.services.llm.base import LLMProvider
from app.services.llm.schemas import (
    AnalysisLLMResponse,
    HUEvaluation,
    ModuleEvaluation,
    ProjectSummarySchema,
)


class FakeProvider(LLMProvider):
    """Proveedor que devuelve siempre una respuesta estructurada fija."""

    def __init__(self, response: AnalysisLLMResponse) -> None:
        self._response = response
        self.calls = 0

    async def complete_structured(self, *, system, prompt, schema):
        self.calls += 1
        return self._response


def _fake_response() -> AnalysisLLMResponse:
    modules = [
        ModuleEvaluation(key="format", score=8.0, issues=["ok"], suggestions=["mejorar X"]),
        ModuleEvaluation(key="invest", score=6.0, issues=["falta criterio"], suggestions=[]),
    ]
    return AnalysisLLMResponse(
        hu_results=[HUEvaluation(hu_id="HU-01", modules=modules)],
        project_summary=ProjectSummarySchema(
            objective="Plataforma de prueba.",
            stakeholders=["Cliente"],
            business_rules=["Regla 1"],
        ),
    )


def test_analyze_maps_structured_response():
    provider = FakeProvider(_fake_response())
    hus = [ParsedHU(hu_id="HU-01", raw_text="Como cliente quiero X para Y")]

    result = asyncio.run(analyze(hus, provider=provider))

    assert provider.calls == 1
    assert len(result.hu_results) == 1
    hu = result.hu_results[0]
    assert hu.hu_id == "HU-01"
    assert 1.0 <= hu.score <= 10.0
    assert "falta criterio" in hu.feedback
    assert "mejorar X" in hu.suggestions
    assert result.project_summary.objective == "Plataforma de prueba."
    assert result.project_summary.stakeholders == ["Cliente"]
    assert 1.0 <= result.overall_score <= 10.0


def test_analyze_empty_raises():
    provider = FakeProvider(_fake_response())
    with pytest.raises(ValueError):
        asyncio.run(analyze([], provider=provider))
