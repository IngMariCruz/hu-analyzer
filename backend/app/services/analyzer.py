"""
Analyzer: orquestador principal del análisis de Historias de Usuario.

Optimizado para mínimo consumo de tokens:
- UN solo llamado a Claude con TODAS las HU y el resumen global
- Modelo Haiku (20x más barato que Sonnet, suficiente para análisis estructurado)
"""

import json
import re
import logging

import anthropic

from app.core.config import settings
from app.services.file_parser import ParsedHU
from app.services.modules import ACTIVE_MODULES
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 16000   # Techo seguro para hasta ~25 HU complejas


def _build_batch_prompt(parsed_hus: list[ParsedHU]) -> str:
    criteria = "\n".join(m.analysis_criteria for m in ACTIVE_MODULES)

    hus_section = "\n\n".join(
        f"### {hu.hu_id}\n{hu.raw_text}" for hu in parsed_hus
    )

    module_keys = {
        m.response_key: {
            "score": "número 0-10",
            "issues": ["observación citando fragmento del texto original"],
            "suggestions": ["sugerencia concreta y aplicable"],
        }
        for m in ACTIVE_MODULES
    }

    response_schema = json.dumps(
        {
            "hu_results": [
                {"hu_id": "HU-XX", **module_keys}
            ],
            "project_summary": {
                "objective": "objetivo general del proyecto en 1-2 oraciones",
                "stakeholders": ["actor 1", "actor 2"],
                "business_rules": ["regla de negocio 1"],
            },
        },
        ensure_ascii=False,
        indent=2,
    )

    return f"""Eres un experto en metodologías ágiles. Analiza las siguientes Historias de Usuario
y extrae también la información global del proyecto.

## Criterios de evaluación por HU

{criteria}

## Historias de Usuario a analizar

{hus_section}

## Formato de respuesta

Responde SOLO con JSON válido con esta estructura exacta.
Incluye una entrada en hu_results por cada HU listada arriba.
No incluyas markdown ni texto fuera del JSON:

{response_schema}
"""


def _extract_json(raw: str) -> dict:
    """Extrae JSON de la respuesta de Claude de forma robusta."""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    logger.error("No se pudo extraer JSON: %s", raw[:300])
    return {}


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


async def analyze(parsed_hus: list[ParsedHU]) -> AnalyzeResponse:
    if not parsed_hus:
        raise ValueError("No se encontraron Historias de Usuario para analizar.")

    logger.info("Analizando %d HU en un solo llamado (modelo: %s)", len(parsed_hus), MODEL)

    response = await _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=(
            "Eres un experto en metodologías ágiles especializado en calidad de "
            "Historias de Usuario. Responde SIEMPRE únicamente con JSON válido, "
            "sin markdown, sin texto adicional."
        ),
        messages=[{"role": "user", "content": _build_batch_prompt(parsed_hus)}],
    )

    data = _extract_json(response.content[0].text)

    hu_results: list[HUResult] = []
    raw_hu_results = data.get("hu_results", [])
    results_by_id = {r.get("hu_id", ""): r for r in raw_hu_results}

    for parsed_hu in parsed_hus:
        hu_data = results_by_id.get(parsed_hu.hu_id, {})

        all_feedback: list[str] = []
        all_suggestions: list[str] = []
        for module in ACTIVE_MODULES:
            module_section = hu_data.get(module.response_key, {})
            all_feedback.extend(module_section.get("issues", []))
            all_suggestions.extend(module_section.get("suggestions", []))

        score = _calculate_weighted_score(hu_data)

        hu_results.append(HUResult(
            hu_id=parsed_hu.hu_id,
            original_text=parsed_hu.raw_text,
            score=score,
            feedback=all_feedback,
            suggestions=all_suggestions,
        ))

    summary_data = data.get("project_summary", {})
    project_summary = ProjectSummary(
        objective=summary_data.get("objective", "No se pudo determinar el objetivo."),
        stakeholders=summary_data.get("stakeholders", []),
        business_rules=summary_data.get("business_rules", []),
    )

    overall = round(sum(r.score for r in hu_results) / len(hu_results), 1)

    logger.info(
        "Análisis completo — %d HU, score global: %s, tokens usados: %s",
        len(hu_results), overall,
        response.usage.input_tokens + response.usage.output_tokens,
    )

    return AnalyzeResponse(
        hu_results=hu_results,
        project_summary=project_summary,
        overall_score=overall,
    )
