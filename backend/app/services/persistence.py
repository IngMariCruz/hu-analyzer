"""
Persistencia de resultados (Story 1.9).

Guarda y recupera análisis SIN el documento, el texto extraído ni PII. Al
recuperar, `original_text` de cada HU NO existe en la base (es texto del
documento) y se devuelve vacío; las bandas se recalculan en lectura.
"""

import uuid

from sqlalchemy.orm import Session

from app.db.models import Analysis, BusinessInference, StoryResult
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary
from app.services.scoring import band_for


def save_analysis(
    db: Session,
    response: AnalyzeResponse,
    *,
    file_type: str,
    duration_ms: int,
    model_version: str,
) -> str:
    """Persiste el análisis (y evento de uso) y devuelve un `analysis_id` opaco.

    No almacena `original_text` de las HU ni ningún texto del documento.
    """
    analysis_id = str(uuid.uuid4())

    analysis = Analysis(
        id=analysis_id,
        status=response.status,
        story_count=response.story_count,
        overall_score=response.overall_score,
        duration_ms=duration_ms,
        model_version=model_version,
        file_type=file_type,
    )

    for index, hu in enumerate(response.hu_results):
        analysis.story_results.append(StoryResult(
            hu_index=index,
            hu_id=hu.hu_id,
            score=hu.score,
            evaluated=hu.evaluated,
            feedback=hu.feedback,
            suggestions=hu.suggestions,
        ))

    summary = response.project_summary
    analysis.business_inference = BusinessInference(
        objective=summary.objective,
        end_users=summary.stakeholders,
        business_rules=summary.business_rules,
    )

    db.add(analysis)
    db.commit()
    return analysis_id


def load_analysis(db: Session, analysis_id: str) -> AnalyzeResponse | None:
    """Recupera un análisis persistido o None si no existe.

    `original_text` de cada HU se devuelve vacío: el texto del documento nunca se
    persiste (privacidad por diseño).
    """
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        return None

    hu_results = [
        HUResult(
            hu_id=sr.hu_id,
            original_text="",
            score=sr.score,
            band=band_for(sr.score),
            evaluated=sr.evaluated,
            feedback=list(sr.feedback or []),
            suggestions=list(sr.suggestions or []),
        )
        for sr in sorted(analysis.story_results, key=lambda r: r.hu_index)
    ]

    inference = analysis.business_inference
    project_summary = ProjectSummary(
        objective=inference.objective if inference else "",
        stakeholders=list(inference.end_users or []) if inference else [],
        business_rules=list(inference.business_rules or []) if inference else [],
    )

    return AnalyzeResponse(
        analysis_id=analysis.id,
        status=analysis.status,
        story_count=analysis.story_count,
        hu_results=hu_results,
        project_summary=project_summary,
        overall_score=analysis.overall_score,
        overall_band=band_for(analysis.overall_score),
    )
