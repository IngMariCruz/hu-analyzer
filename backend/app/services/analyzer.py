"""
Analyzer: orquestador principal del análisis de Historias de Usuario.

Responsabilidades:
1. Construir el prompt compuesto con los criterios de todos los módulos activos
2. Hacer UN solo llamado a Claude por cada HU
3. Distribuir la respuesta a cada módulo para que parsee su sección
4. Calcular la calificación final ponderada
5. Hacer UN llamado adicional para extraer info global del proyecto
6. Retornar un AnalyzeResponse completo
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

# ── Cliente Anthropic (singleton) ───────────────────────────────────────────
_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 2048


# ── Helpers de prompt ────────────────────────────────────────────────────────

def _build_hu_prompt(hu_text: str) -> str:
    """
    Construye el prompt de análisis individual inyectando los criterios
    de todos los módulos activos y el esquema de respuesta esperado.
    """
    criteria = "\n".join(m.analysis_criteria for m in ACTIVE_MODULES)

    response_schema = json.dumps(
        {
            m.response_key: {
                "score": "número del 0 al 10",
                "issues": ["observación citando fragmento del texto original"],
                "suggestions": ["sugerencia concreta y aplicable"],
            }
            for m in ACTIVE_MODULES
        },
        ensure_ascii=False,
        indent=2,
    )

    return f"""Analiza la siguiente Historia de Usuario evaluando cada criterio indicado.
Cita fragmentos exactos del texto original en los issues para que el equipo pueda localizar el problema.

## Criterios de evaluación

{criteria}

## Formato de respuesta requerido

Responde SOLO con JSON válido con esta estructura exacta.
No incluyas markdown, no incluyas texto antes ni después del JSON:

{response_schema}

## Historia de Usuario a analizar

{hu_text}
"""


def _build_global_prompt(all_texts: list[str]) -> str:
    """
    Construye el prompt para extraer información global del proyecto
    a partir del conjunto completo de HU.
    """
    combined = "\n\n---\n\n".join(all_texts)

    return f"""Analiza el siguiente conjunto de Historias de Usuario de un proyecto de software.
Extrae la información estratégica global.

## Historias de Usuario del proyecto

{combined}

## Formato de respuesta requerido

Responde SOLO con JSON válido con esta estructura exacta.
No incluyas markdown, no incluyas texto antes ni después del JSON:

{{
  "objective": "objetivo general del proyecto en 1-2 oraciones claras",
  "stakeholders": ["actor o usuario 1", "actor o usuario 2"],
  "business_rules": [
    "regla de negocio detectada 1",
    "regla de negocio detectada 2"
  ]
}}
"""


# ── Parser de respuesta JSON ─────────────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    """
    Extrae JSON de la respuesta de Claude de forma robusta.
    Maneja casos donde Claude incluye markdown o texto adicional.
    """
    # Intentar parsear directamente
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # Buscar bloque JSON entre ```json ... ``` o ``` ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Buscar primer objeto JSON en el texto
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    logger.error("No se pudo extraer JSON de la respuesta: %s", raw[:200])
    return {}


# ── Llamadas a Claude ────────────────────────────────────────────────────────

async def _call_claude(system: str, user: str) -> dict:
    """Realiza un llamado a la API de Claude y retorna el JSON parseado."""
    response = await _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = response.content[0].text
    return _extract_json(raw)


# ── Cálculo de calificación ──────────────────────────────────────────────────

def _calculate_weighted_score(module_results: list) -> float:
    """Calcula el promedio ponderado de todos los módulos."""
    total = sum(r.score * r.weight for r in module_results)
    total_weight = sum(r.weight for r in module_results)
    if total_weight == 0:
        return 5.0
    raw = total / total_weight
    return round(max(1.0, min(10.0, raw)), 1)


# ── Análisis por HU ──────────────────────────────────────────────────────────

async def _analyze_single_hu(parsed_hu: ParsedHU) -> HUResult:
    """
    Analiza una HU individual:
    1. Llama a Claude con el prompt compuesto
    2. Pasa la respuesta a cada módulo para que parsee su sección
    3. Calcula la calificación ponderada final
    """
    system = (
        "Eres un experto en metodologías ágiles especializado en calidad de "
        "Historias de Usuario. Analizas HU con criterios rigurosos y retornas "
        "retroalimentación detallada citando fragmentos del texto original. "
        "Responde SIEMPRE únicamente con JSON válido, sin markdown, sin texto adicional."
    )

    response_data = await _call_claude(system, _build_hu_prompt(parsed_hu.raw_text))

    # Cada módulo parsea su sección
    module_results = []
    all_feedback: list[str] = []
    all_suggestions: list[str] = []

    for module in ACTIVE_MODULES:
        module_data = response_data.get(module.response_key, {})
        result = module.parse_response(module_data)
        module_results.append(result)
        all_feedback.extend(result.issues)
        all_suggestions.extend(result.suggestions)

    score = _calculate_weighted_score(module_results)

    return HUResult(
        hu_id=parsed_hu.hu_id,
        original_text=parsed_hu.raw_text,
        score=score,
        feedback=all_feedback,
        suggestions=all_suggestions,
    )


# ── Extracción global del proyecto ───────────────────────────────────────────

async def _extract_project_summary(all_texts: list[str]) -> ProjectSummary:
    """
    Extrae objetivo, stakeholders y reglas de negocio del conjunto completo de HU.
    """
    system = (
        "Eres un experto en análisis de requisitos de software. "
        "Extraes información estratégica del conjunto de Historias de Usuario. "
        "Responde SIEMPRE únicamente con JSON válido, sin markdown, sin texto adicional."
    )

    data = await _call_claude(system, _build_global_prompt(all_texts))

    return ProjectSummary(
        objective=data.get("objective", "No se pudo determinar el objetivo del proyecto."),
        stakeholders=data.get("stakeholders", []),
        business_rules=data.get("business_rules", []),
    )


# ── Punto de entrada principal ───────────────────────────────────────────────

async def analyze(parsed_hus: list[ParsedHU]) -> AnalyzeResponse:
    """
    Orquesta el análisis completo de un conjunto de HU.

    Args:
        parsed_hus: lista de HU extraídas por FileParser.

    Returns:
        AnalyzeResponse con resultados individuales y resumen global.

    Raises:
        anthropic.APIError: si falla la comunicación con Claude.
    """
    if not parsed_hus:
        raise ValueError("No se encontraron Historias de Usuario para analizar.")

    # Analizar cada HU individualmente
    hu_results: list[HUResult] = []
    for parsed_hu in parsed_hus:
        logger.info("Analizando %s...", parsed_hu.hu_id)
        result = await _analyze_single_hu(parsed_hu)
        hu_results.append(result)

    # Calificación global (promedio simple de todas las HU)
    overall = round(
        sum(r.score for r in hu_results) / len(hu_results), 1
    )

    # Extracción global del proyecto
    all_texts = [hu.raw_text for hu in parsed_hus]
    project_summary = await _extract_project_summary(all_texts)

    return AnalyzeResponse(
        hu_results=hu_results,
        project_summary=project_summary,
        overall_score=overall,
    )
