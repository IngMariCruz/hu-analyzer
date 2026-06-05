from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.routes import analyze

# ── Metadata de tags (aparece como secciones en Swagger) ───────────────────
tags_metadata = [
    {
        "name": "Análisis",
        "description": "Endpoints para analizar archivos con Historias de Usuario.",
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

### Formatos soportados
`.docx` · `.pdf` · `.xlsx` · `.txt`

### Criterios de evaluación
- Formato: `Como <usuario> quiero <funcionalidad> para <objetivo>`
- Usuario válido (no QA, no equipo de desarrollo)
- Una sola funcionalidad por HU
- Criterios de aceptación bajo principio **INVEST**
- Coherencia y ausencia de ambigüedad
""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Equipo HU Analyzer",
        "email": "soporte@hu-analyzer.dev",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc (vista alternativa)
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ──────────────────────────────────────────────────────────────────
app.include_router(analyze.router, prefix="/api/v1")


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verificar estado del servidor",
    response_description="Estado y versión actual de la API",
)
async def health_check():
    """Retorna el estado operativo del servidor y la versión de la API."""
    return {"status": "ok", "version": "1.0.0"}
