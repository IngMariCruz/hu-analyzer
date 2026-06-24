from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import init_db
from app.api.v1.routes import admin, analyze, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

tags_metadata = [
    {
        "name": "Análisis",
        "description": "Endpoints para analizar archivos con HU y generar reportes.",
    },
    {
        "name": "Admin",
        "description": "Panel de administrador (JWT): métricas de uso y resultados, sin documentos.",
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

- 📊 **Calificación (1–100)** y banda por cada Historia de Usuario
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
    lifespan=lifespan,
)

# Rate-limiting efímero por IP (Story 1.11)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health", tags=["Sistema"], summary="Verificar estado del servidor")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
