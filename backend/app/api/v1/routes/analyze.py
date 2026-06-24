import logging
import time

import openai
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models.schemas import AnalyzeResponse, ErrorResponse, ProjectSummary
from app.services.file_parser import parse_file
from app.services.gate import check_document
from app.services.analyzer import analyze
from app.services.persistence import save_analysis, load_analysis


def _gate_response(status_value: str, message: str) -> AnalyzeResponse:
    """Respuesta cuando el gate detiene el análisis (no_project / invalid / sin HU)."""
    return AnalyzeResponse(
        status=status_value,
        message=message,
        story_count=0,
        hu_results=[],
        project_summary=ProjectSummary(objective="", stakeholders=[], business_rules=[]),
        overall_score=0.0,
        overall_band="",
    )

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/plain": ".txt",
}


@router.post(
    "/analyze",
    tags=["Análisis"],
    summary="Analizar archivo con Historias de Usuario",
    response_description="Calificaciones, retroalimentación y resumen del proyecto",
    response_model=AnalyzeResponse,
    responses={
        200: {"description": "Análisis completado exitosamente.", "model": AnalyzeResponse},
        422: {
            "description": "Archivo inválido o tipo no soportado.",
            "model": ErrorResponse,
            "content": {"application/json": {"example": {
                "detail": "Tipo de archivo no soportado: application/zip. Use .docx, .pdf, .xlsx o .txt",
                "code": "UNSUPPORTED_FILE_TYPE",
            }}},
        },
        413: {
            "description": "El archivo supera el tamaño máximo permitido.",
            "model": ErrorResponse,
            "content": {"application/json": {"example": {
                "detail": "El archivo supera el tamaño máximo de 10 MB.",
                "code": "FILE_TOO_LARGE",
            }}},
        },
        429: {
            "description": "Se superó el límite de solicitudes (rate-limit).",
            "model": ErrorResponse,
        },
        500: {
            "description": "Error interno del servidor.",
            "model": ErrorResponse,
            "content": {"application/json": {"example": {
                "detail": "Error al procesar el archivo. Intente nuevamente.",
                "code": "INTERNAL_ERROR",
            }}},
        },
    },
)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_file(
    request: Request,
    file: UploadFile = File(
        ...,
        description=(
            "Archivo con las Historias de Usuario. "
            "Formatos aceptados: .docx, .pdf, .xlsx, .txt. "
            "Tamaño máximo: 10 MB."
        ),
    ),
    db: Session = Depends(get_db),
):
    """
    Recibe un archivo con Historias de Usuario redactadas y retorna:

    - **Calificación (1–100)** y banda por cada HU encontrada
    - **Retroalimentación** con observaciones específicas
    - **Sugerencias** de mejora para las HU con calificación < 90
    - **Objetivo, usuarios finales y reglas de negocio** inferidos (abstraídos)
    - **`analysis_id`** opaco para recuperar el resultado en sesión

    El documento se procesa en memoria y nunca se almacena.
    """
    # 1. Validar tipo de archivo (antes de procesar — tope de tipo, Story 1.11)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Tipo de archivo no soportado: {file.content_type}. "
                f"Use {', '.join(ALLOWED_CONTENT_TYPES.values())}"
            ),
        )

    # 2. Validar tamaño (antes de procesar — tope de tamaño, Story 1.11)
    file.file.seek(0, 2)
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # 3. Parsear archivo y segmentar HU
    try:
        parse_result = await parse_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    started = time.perf_counter()

    # 4. Gate de pertinencia/validez y análisis híbrido
    try:
        gate = await check_document(parse_result.raw_text)
        if gate.status != "ok":
            result = _gate_response(gate.status, gate.message)
        elif parse_result.total_found == 0:
            result = _gate_response(
                "ok", "No se detectaron Historias de Usuario en el documento."
            )
        else:
            result = await analyze(parse_result.hus)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except openai.AuthenticationError:
        logger.error("API key de OpenAI inválida o expirada.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de autenticación con el servicio de IA. Contacte al administrador.",
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se alcanzó el límite de solicitudes. Intente nuevamente en unos momentos.",
        )
    except openai.APIError as exc:
        logger.error("Error de API OpenAI: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al comunicarse con el servicio de IA. Intente nuevamente.",
        )

    # 5. Persistir resultado (también es el evento de uso, FR28) y devolver id opaco
    duration_ms = int((time.perf_counter() - started) * 1000)
    try:
        analysis_id = save_analysis(
            db,
            result,
            file_type=parse_result.source_type,
            duration_ms=duration_ms,
            model_version=settings.LLM_MODEL,
        )
        result.analysis_id = analysis_id
    except Exception as exc:  # noqa: BLE001 — no perder el resultado por un fallo de DB
        logger.error("No se pudo persistir el análisis: %s", type(exc).__name__)

    return result


@router.get(
    "/analyze/{analysis_id}",
    tags=["Análisis"],
    summary="Recuperar un análisis por su identificador",
    response_model=AnalyzeResponse,
    responses={
        200: {"description": "Análisis recuperado.", "model": AnalyzeResponse},
        404: {"description": "El análisis no existe o ya no está disponible.", "model": ErrorResponse},
    },
)
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Recupera el resultado persistido. El texto original del documento no se
    devuelve (nunca se almacenó)."""
    result = load_analysis(db, analysis_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El análisis solicitado no existe o ya no está disponible.",
        )
    return result
