from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.routes import analyze, report

tags_metadata = [
    {
        "name": "Análisis",
        "description": "Endpoints para analizar archivos con HU y generar reportes.",
    },
    {
        "name": "Sistema",
        "description": "Endpoints de estado y salud del servidor.",
    },
]

app = FastAPI(
    title="HU Analyzer API",
    description="""
## Sistema de análisis de Historias de Usuario con IA

Sube un archivo con tus HU y obtén:

- 📊 **Calificación (1–10)** por cada Historia de Usuario
- 💬 **Retroalimentación detallada** con citas del texto original
- ✏️ **Sugerencias de mejora** concretas
- 🎯 **Objetivo del proyecto** inferido del conjunto de HU
- 👥 **Stakeholders identificados**
- 📋 **Reglas de negocio** detectadas
- 📄 **Reporte PDF** descargable

### Formatos soportados
`.docx` · `.pdf` · `.xlsx` · `.txt`
""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={"name": "Equipo HU Analyzer", "email": "soporte@hu-analyzer.dev"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")


@app.get("/health", tags=["Sistema"], summary="Verificar estado del servidor")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
