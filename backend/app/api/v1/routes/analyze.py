from fastapi import APIRouter, HTTPException, UploadFile, File, status
from app.models.schemas import AnalyzeResponse, ErrorResponse
from app.services.file_parser import parse_file
from app.core.config import settings

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
        200: {
            "description": "Análisis completado exitosamente.",
            "model": AnalyzeResponse,
        },
        422: {
            "description": "Archivo inválido o tipo no soportado.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Tipo de archivo no soportado: application/zip. Use .docx, .pdf, .xlsx o .txt",
                        "code": "UNSUPPORTED_FILE_TYPE",
                    }
                }
            },
        },
        413: {
            "description": "El archivo supera el tamaño máximo permitido (10 MB).",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El archivo supera el tamaño máximo de 10 MB.",
                        "code": "FILE_TOO_LARGE",
                    }
                }
            },
        },
        500: {
            "description": "Error interno del servidor.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error al procesar el archivo. Intente nuevamente.",
                        "code": "INTERNAL_ERROR",
                    }
                }
            },
        },
    },
)
async def analyze_file(
    file: UploadFile = File(
        ...,
        description="Archivo con las Historias de Usuario. Formatos aceptados: .docx, .pdf, .xlsx, .txt. Tamaño máximo: 10 MB.",
    ),
):
    """
    Recibe un archivo con Historias de Usuario redactadas y retorna:

    - **Calificación (1–10)** por cada HU encontrada
    - **Retroalimentación** con observaciones específicas citando el texto original
    - **Sugerencias** de mejora concretas y aplicables
    - **Objetivo del proyecto** inferido del conjunto de HU
    - **Stakeholders** identificados
    - **Reglas de negocio** detectadas

    ### Criterios de evaluación por HU
    - ✅ Formato: `Como <usuario> quiero <funcionalidad> para <objetivo>`
    - ✅ El usuario no es QA, desarrollador ni equipo técnico
    - ✅ Una sola funcionalidad por HU
    - ✅ Objetivo claro y medible
    - ✅ Criterios de aceptación bajo principio INVEST
    - ✅ Coherencia y ausencia de ambigüedad
    """
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de archivo no soportado: {file.content_type}. "
                   f"Use {', '.join(ALLOWED_CONTENT_TYPES.values())}",
        )

    # Validar tamaño del archivo
    file.file.seek(0, 2)
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # Parsear archivo y segmentar HU
    try:
        parse_result = await parse_file(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # TODO: Sesión 4 — invocar módulos de análisis por cada HU
    # TODO: Sesión 5 — invocar Analyzer con Claude API y extracción global

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Parser OK — {parse_result.total_found} HU encontradas en archivo {parse_result.source_type}. Módulo de análisis en construcción.",
    )
