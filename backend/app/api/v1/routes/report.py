from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.models.schemas import AnalyzeResponse
from app.services.pdf_generator import generate_pdf

router = APIRouter()


@router.post(
    "/report",
    tags=["Análisis"],
    summary="Generar reporte PDF del análisis",
    response_description="Archivo PDF con el reporte completo",
    responses={
        200: {
            "description": "PDF generado exitosamente.",
            "content": {"application/pdf": {}},
        },
        500: {"description": "Error al generar el PDF."},
    },
)
async def generate_report(result: AnalyzeResponse):
    """
    Recibe el resultado de un análisis y retorna un PDF descargable con:
    - Portada con score global
    - Resumen del proyecto (objetivo, stakeholders, reglas de negocio)
    - Análisis detallado por HU con observaciones y sugerencias
    """
    try:
        pdf_bytes = generate_pdf(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte-hu-analyzer.pdf"},
    )
