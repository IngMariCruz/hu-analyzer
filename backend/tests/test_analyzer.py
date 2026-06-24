"""
Pruebas del orquestador híbrido `analyze` con un proveedor LLM falso (sin red).
"""

import asyncio

import pytest

from app.services.analyzer import analyze
from app.services.file_parser import ParsedHU
from app.services.llm.base import LLMProvider
from app.services.llm.schemas import (
    BusinessInferenceResponse,
    HUEvaluationResponse,
    ModuleEvaluation,
)


class FakeProvider(LLMProvider):
    """Proveedor falso que despacha según el `schema` solicitado.

    Permite simular fallo en la evaluación por-HU (para `status: partial`).
    """

    def __init__(self, *, fail_hu_eval: bool = False) -> None:
        self.fail_hu_eval = fail_hu_eval
        self.hu_calls = 0
        self.inference_calls = 0

    async def complete_structured(self, *, system, prompt, schema):
        if schema is HUEvaluationResponse:
            self.hu_calls += 1
            if self.fail_hu_eval:
                raise TimeoutError("simulado")
            return HUEvaluationResponse(modules=[
                ModuleEvaluation(key="format", score=8.0, issues=["ok"], suggestions=["mejorar X"]),
                ModuleEvaluation(key="invest", score=6.0, issues=["falta criterio"], suggestions=[]),
            ])
        if schema is BusinessInferenceResponse:
            self.inference_calls += 1
            return BusinessInferenceResponse(
                objective="Plataforma de prueba.",
                end_users=["Cliente"],
                business_rules=["Regla 1"],
            )
        raise AssertionError(f"schema inesperado: {schema}")


def test_analyze_maps_structured_response():
    provider = FakeProvider()
    hus = [
        ParsedHU(hu_id="HU-01", raw_text="Como cliente quiero X para Y"),
        ParsedHU(hu_id="HU-02", raw_text="Como cliente quiero Z para W"),
    ]

    result = asyncio.run(analyze(hus, provider=provider))

    assert provider.hu_calls == 2          # 1 llamada por HU
    assert provider.inference_calls == 1   # 1 llamada nivel-documento
    assert result.status == "ok"
    assert len(result.hu_results) == 2
    hu = result.hu_results[0]
    assert hu.hu_id == "HU-01"
    assert 1 <= hu.score <= 100
    assert hu.band in {"Excepcional", "Bueno", "Regular", "Crítico"}
    assert hu.evaluated is True
    assert "falta criterio" in hu.feedback
    assert result.project_summary.objective == "Plataforma de prueba."
    assert result.project_summary.stakeholders == ["Cliente"]
    assert 1 <= result.overall_score <= 100
    assert result.overall_band == hu.band or result.overall_band  # banda calculada


def test_analyze_marks_partial_when_hu_fails():
    provider = FakeProvider(fail_hu_eval=True)
    hus = [ParsedHU(hu_id="HU-01", raw_text="Como cliente quiero X para Y")]

    result = asyncio.run(analyze(hus, provider=provider))

    assert result.status == "partial"
    assert result.hu_results[0].evaluated is False
    assert result.overall_score == 0.0   # las HU no evaluadas no cuentan en el promedio


def test_analyze_suggestions_only_below_90():
    """Una HU con score >= 90 no debe llevar sugerencias (Story 1.7)."""
    class HighScoreProvider(FakeProvider):
        async def complete_structured(self, *, system, prompt, schema):
            if schema is HUEvaluationResponse:
                return HUEvaluationResponse(modules=[
                    ModuleEvaluation(key="format", score=10.0, issues=[], suggestions=["x"]),
                    ModuleEvaluation(key="invest", score=10.0, issues=[], suggestions=["y"]),
                    ModuleEvaluation(key="user", score=10.0, issues=[], suggestions=[]),
                    ModuleEvaluation(key="functionality", score=10.0, issues=[], suggestions=[]),
                    ModuleEvaluation(key="coherence", score=10.0, issues=[], suggestions=[]),
                ])
            return await super().complete_structured(system=system, prompt=prompt, schema=schema)

    provider = HighScoreProvider()
    hus = [ParsedHU(hu_id="HU-01", raw_text="Como cliente quiero X para Y")]
    result = asyncio.run(analyze(hus, provider=provider))

    assert result.hu_results[0].score >= 90
    assert result.hu_results[0].suggestions == []


def test_analyze_empty_raises():
    provider = FakeProvider()
    with pytest.raises(ValueError):
        asyncio.run(analyze([], provider=provider))
