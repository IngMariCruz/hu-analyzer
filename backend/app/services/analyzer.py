"""
Analyzer: orquestador híbrido del análisis de Historias de Usuario (Story 1.5).

Orquestación:
- 1 llamada nivel-documento para la inferencia de negocio (objetivo, usuarios
  finales, reglas de negocio) — ver `inference.py`.
- 1 llamada por HU en paralelo (`asyncio.gather` + semáforo) para su evaluación.

El proveedor LLM aplica backoff en 429/5xx/timeout (SDK `max_retries`). Si una
HU sigue fallando tras los reintentos, se marca esa HU sin abortar el resto y el
documento queda en `status: partial`. La normalización de score (1–100) y las
bandas viven en la capa de agregación (`scoring.py`), no aquí.
"""

import asyncio
import logging

from app.core.config import settings
from app.services.file_parser import ParsedHU
from app.services.inference import infer_business
from app.services.modules import ACTIVE_MODULES
from app.services.scoring import aggregate_hu_score, band_for, overall_average
from app.services.llm import LLMProvider, get_llm_provider
from app.services.llm.schemas import HUEvaluationResponse
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary

logger = logging.getLogger(__name__)

# Score por debajo del cual el sistema genera sugerencias de mejora (Story 1.7).
SUGGESTION_THRESHOLD = 90

_SYSTEM_PROMPT = (
    "Eres un experto en metodologías ágiles especializado en calidad de "
    "Historias de Usuario. Devuelve únicamente la información solicitada en el "
    "esquema estructurado, sin texto adicional."
)


def _build_hu_prompt(hu: ParsedHU) -> str:
    criteria = "\n".join(m.analysis_criteria for m in ACTIVE_MODULES)
    valid_keys = ", ".join(m.response_key for m in ACTIVE_MODULES)

    return f"""Evalúa la siguiente Historia de Usuario según cada criterio.

## Criterios de evaluación

{criteria}

## Historia de Usuario

{hu.raw_text}

## Instrucciones de respuesta

Devuelve `modules` con UNA entrada por cada criterio. Usa como `key` exactamente
uno de: {valid_keys}. Cada módulo lleva `score` (0–10), `issues` (observaciones
citando el texto) y `suggestions` (mejoras concretas y aplicables). Si la HU es
excelente en un criterio, deja `issues` y `suggestions` vacíos para ese módulo.
"""


async def _evaluate_hu(
    hu: ParsedHU,
    provider: LLMProvider,
    semaphore: asyncio.Semaphore,
) -> HUEvaluationResponse | None:
    """Evalúa una HU; devuelve None si falla tras los reintentos del proveedor."""
    async with semaphore:
        try:
            return await provider.complete_structured(
                system=_SYSTEM_PROMPT,
                prompt=_build_hu_prompt(hu),
                schema=HUEvaluationResponse,
            )
        except Exception as exc:  # noqa: BLE001 — degradar esta HU, no abortar el resto
            logger.warning(
                "Falló la evaluación de la HU %s tras reintentos: %s",
                hu.hu_id, type(exc).__name__,
            )
            return None


def _build_hu_result(hu: ParsedHU, evaluation: HUEvaluationResponse | None) -> HUResult:
    if evaluation is None:
        return HUResult(
            hu_id=hu.hu_id,
            original_text=hu.raw_text,
            score=1,
            band=band_for(1),
            evaluated=False,
            feedback=["No se pudo evaluar esta HU; intente reanalizar el documento."],
            suggestions=[],
        )

    module_data: dict[str, dict] = {}
    feedback: list[str] = []
    suggestions: list[str] = []
    for module in evaluation.modules:
        module_data[module.key] = {
            "score": module.score,
            "issues": module.issues,
            "suggestions": module.suggestions,
        }
        feedback.extend(module.issues)
        suggestions.extend(module.suggestions)

    score = aggregate_hu_score(module_data)
    # Story 1.7: solo las HU con score < 90 requieren sugerencias.
    if score >= SUGGESTION_THRESHOLD:
        suggestions = []

    return HUResult(
        hu_id=hu.hu_id,
        original_text=hu.raw_text,
        score=score,
        band=band_for(score),
        evaluated=True,
        feedback=feedback,
        suggestions=suggestions,
    )


async def analyze(
    parsed_hus: list[ParsedHU],
    provider: LLMProvider | None = None,
) -> AnalyzeResponse:
    """Analiza un conjunto de HU con orquestación híbrida y arma la respuesta.

    Args:
        parsed_hus: HU segmentadas del documento.
        provider: proveedor LLM a usar; por defecto el configurado.

    Returns:
        AnalyzeResponse con el resultado por HU y la inferencia de negocio.
        `status` es `partial` si alguna HU no pudo evaluarse.

    Raises:
        ValueError: si no hay HU que analizar.
    """
    if not parsed_hus:
        raise ValueError("No se encontraron Historias de Usuario para analizar.")

    provider = provider or get_llm_provider()
    semaphore = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)

    logger.info(
        "Analizando %d HU (concurrencia=%d) + inferencia de negocio.",
        len(parsed_hus), settings.LLM_MAX_CONCURRENCY,
    )

    evaluations, inference = await asyncio.gather(
        asyncio.gather(*(_evaluate_hu(hu, provider, semaphore) for hu in parsed_hus)),
        infer_business(parsed_hus, provider=provider),
    )

    hu_results = [_build_hu_result(hu, ev) for hu, ev in zip(parsed_hus, evaluations)]

    evaluated_scores = [r.score for r in hu_results if r.evaluated]
    overall = overall_average(evaluated_scores)
    any_failed = any(not r.evaluated for r in hu_results)

    project_summary = ProjectSummary(
        objective=inference.objective or "No se pudo determinar el objetivo.",
        stakeholders=inference.end_users,
        business_rules=inference.business_rules,
    )

    logger.info(
        "Análisis completo — %d HU, promedio: %s, status: %s",
        len(hu_results), overall, "partial" if any_failed else "ok",
    )

    return AnalyzeResponse(
        status="partial" if any_failed else "ok",
        story_count=len(hu_results),
        hu_results=hu_results,
        project_summary=project_summary,
        overall_score=overall,
        overall_band=band_for(overall),
    )
