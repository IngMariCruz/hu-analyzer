from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.routes import analyze

app = FastAPI(
    title="HU Analyzer",
    description="Sistema de análisis y calificación de Historias de Usuario con IA",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(analyze.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Verifica que el servidor esté corriendo."""
    return {"status": "ok", "version": "1.0.0"}
