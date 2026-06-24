from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import AnalyzeResponse, ErrorResponse
from app.services.pdf_generator import (
    build_business_report,
    build_hu_report,
    generate_pdf,
)
from app.services.persistence import load_analysis

router = APIRouter()

# Tipo de reporte → (builder, nombre de archivo)
_REPORTS = {
    "business": (build_business_report, "reglas-de-negocio"),
    "hu": (build_hu_report, "validacion-hus"),
}


@router.get(
    "/report/{analysis_id}",
    tags=["Análisis"],
    summary="Descargar un reporte PDF del análisis persistido",
    response_description="Archivo PDF del reporte solicitado",
    responses={
        200: {"description": "PDF generado.", "content": {"application/pdf": {}}},
        404: {"description": "El análisis no existe o ya no está disponible.", "model": ErrorResponse},
        422: {"description": "Tipo de reporte inválido.", "model": ErrorResponse},
    },
)
async def download_report(
    analysis_id: str,
    type: str = Query("business", description="Tipo de reporte: 'business' o 'hu'."),
    db: Session = Depends(get_db),
):
    """Genera el PDF SOLO desde el resultado persistido (nunca re-lee el documento).

    - `type=business`: objetivo, usuarios finales y reglas de negocio.
    - `type=hu`: calificación por HU (score, banda, observaciones, sugerencias) + general.
    """
    if type not in _REPORTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tipo de reporte inválido. Use 'business' o 'hu'.",
        )

    result = load_analysis(db, analysis_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El análisis solicitado no existe o ya no está disponible.",
        )

    builder, name = _REPORTS[type]
    try:
        pdf_bytes = builder(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {exc}",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={name}-{analysis_id[:8]}.pdf"},
    )


@router.post(
    "/report",
    tags=["Análisis"],
    summary="Generar reporte PDF combinado (descarga en sesión)",
    response_description="Archivo PDF con el reporte completo",
    responses={
        200: {"description": "PDF generado exitosamente.", "content": {"application/pdf": {}}},
        500: {"description": "Error al generar el PDF."},
    },
)
async def generate_report(result: AnalyzeResponse):
    """Reporte combinado a partir del resultado en sesión (sin re-subir el archivo)."""
    try:
        pdf_bytes = generate_pdf(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {exc}",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte-hu-analyzer.pdf"},
    )
