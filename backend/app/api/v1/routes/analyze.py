from fastapi import APIRouter, HTTPException, UploadFile, File, status
from app.models.schemas import AnalyzeResponse

router = APIRouter()

ALLOWED_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",        # .xlsx
    "text/plain",
}


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analiza un archivo con Historias de Usuario",
    responses={
        422: {"description": "Archivo inválido o tipo no soportado"},
        500: {"description": "Error interno del servidor"},
    },
)
async def analyze_file(file: UploadFile = File(...)):
    """
    Recibe un archivo (.docx, .pdf, .xlsx, .txt) con Historias de Usuario,
    lo analiza y retorna calificaciones, retroalimentación y resumen del proyecto.
    """
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de archivo no soportado: {file.content_type}. "
                   "Use .docx, .pdf, .xlsx o .txt",
        )

    # TODO: Sesión 3 — invocar FileParser
    # TODO: Sesión 4 — invocar módulos de análisis
    # TODO: Sesión 5 — invocar Analyzer con Claude API

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Módulo de análisis en construcción",
    )
