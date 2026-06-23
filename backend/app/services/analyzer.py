"""
Analyzer: orquestador principal del análisis de Historias de Usuario.

Un solo llamado al proveedor LLM (GPT-4o mini por defecto) con todas las HU y
el resumen global, usando salida estructurada (Structured Outputs) para
garantizar JSON válido. El proveedor es inyectable para pruebas.
"""

import logging

from app.services.file_parser import ParsedHU
from app.services.modules import ACTIVE_MODULES
from app.services.llm import LLMProvider, get_llm_provider
from app.services.llm.schemas import AnalysisLLMResponse
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Eres un experto en metodologías ágiles especializado en calidad de "
    "Historias de Usuario. Devuelve únicamente la información solicitada en el "
    "esquema estructurado, sin texto adicional."
)


def _build_batch_prompt(parsed_hus: list[ParsedHU]) -> str:
    criteria = "\n".join(m.analysis_criteria for m in ACTIVE_MODULES)
    valid_keys = ", ".join(m.response_key for m in ACTIVE_MODULES)
    hus_section = "\n\n".join(f"### {hu.hu_id}\n{hu.raw_text}" for hu in parsed_hus)

    return f"""Analiza las siguientes Historias de Usuario y extrae también la
información global del proyecto.

## Criterios de evaluación por HU

{criteria}

## Historias de Usuario a analizar

{hus_section}

## Instrucciones de respuesta

Por cada HU listada arriba devuelve una entrada en `hu_results` con su `hu_id`
exacto y una lista `modules` con UNA entrada por cada criterio. Usa como `key`
exactamente uno de: {valid_keys}. Cada módulo lleva `score` (0-10), `issues`
(observaciones citando el texto) y `suggestions` (mejoras concretas). Incluye
además `project_summary` con objetivo, stakeholders y reglas de negocio.
"""


def _calculate_weighted_score(module_data: dict) -> float:
    total = 0.0
    total_weight = 0.0
    for module in ACTIVE_MODULES:
        data = module_data.get(module.response_key, {})
        score = float(data.get("score", 5.0))
        total += score * module.weight
        total_weight += module.weight
    if total_weight == 0:
        return 5.0
    return round(max(1.0, min(10.0, total / total_weight)), 1)


async def analyze(
    parsed_hus: list[ParsedHU],
    provider: LLMProvider | None = None,
) -> AnalyzeResponse:
    """Analiza un conjunto de HU con el proveedor LLM y arma la respuesta.

    Args:
        parsed_hus: HU segmentadas del documento.
        provider: proveedor LLM a usar; por defecto el configurado.

    Returns:
        AnalyzeResponse con el resultado por HU y el resumen del proyecto.

    Raises:
        ValueError: si no hay HU que analizar.
    """
    if not parsed_hus:
        raise ValueError("No se encontraron Historias de Usuario para analizar.")

    provider = provider or get_llm_provider()

    logger.info("Analizando %d HU en un solo llamado estructurado.", len(parsed_hus))

    data: AnalysisLLMResponse = await provider.complete_structured(
        system=_SYSTEM_PROMPT,
        prompt=_build_batch_prompt(parsed_hus),
        schema=AnalysisLLMResponse,
    )

    results_by_id = {hu.hu_id: hu for hu in data.hu_results}

    hu_results: list[HUResult] = []
    for parsed_hu in parsed_hus:
        evaluation = results_by_id.get(parsed_hu.hu_id)

        module_data: dict[str, dict] = {}
        all_feedback: list[str] = []
        all_suggestions: list[str] = []
        if evaluation is not None:
            for module in evaluation.modules:
                module_data[module.key] = {
                    "score": module.score,
                    "issues": module.issues,
                    "suggestions": module.suggestions,
                }
                all_feedback.extend(module.issues)
                all_suggestions.extend(module.suggestions)

        hu_results.append(HUResult(
            hu_id=parsed_hu.hu_id,
            original_text=parsed_hu.raw_text,
            score=_calculate_weighted_score(module_data),
            feedback=all_feedback,
            suggestions=all_suggestions,
        ))

    summary = data.project_summary
    project_summary = ProjectSummary(
        objective=summary.objective or "No se pudo determinar el objetivo.",
        stakeholders=summary.stakeholders,
        business_rules=summary.business_rules,
    )

    overall = round(sum(r.score for r in hu_results) / len(hu_results), 1)

    logger.info("Análisis completo — %d HU, score global: %s", len(hu_results), overall)

    return AnalyzeResponse(
        hu_results=hu_results,
        project_summary=project_summary,
        overall_score=overall,
    )
