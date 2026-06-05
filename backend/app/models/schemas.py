from pydantic import BaseModel, Field


# ── Resultado por Historia de Usuario ──────────────────────────────────────

class HUResult(BaseModel):
    hu_id: str = Field(..., description="Identificador de la HU (ej: HU-01)")
    original_text: str = Field(..., description="Texto original extraído del archivo")
    score: float = Field(..., ge=1.0, le=10.0, description="Calificación de 1 a 10")
    feedback: list[str] = Field(
        default_factory=list,
        description="Observaciones con citas del texto original",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Sugerencias concretas de mejora",
    )


# ── Resumen del proyecto ────────────────────────────────────────────────────

class ProjectSummary(BaseModel):
    objective: str = Field(..., description="Objetivo general del proyecto inferido de las HU")
    stakeholders: list[str] = Field(
        default_factory=list,
        description="Actores/usuarios identificados en las HU",
    )
    business_rules: list[str] = Field(
        default_factory=list,
        description="Reglas de negocio detectadas en las HU",
    )


# ── Respuesta completa del análisis ────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    hu_results: list[HUResult] = Field(
        default_factory=list,
        description="Análisis individual por cada HU encontrada",
    )
    project_summary: ProjectSummary = Field(
        ..., description="Información global extraída del conjunto de HU",
    )
    overall_score: float = Field(
        ..., ge=1.0, le=10.0,
        description="Promedio ponderado de todas las calificaciones",
    )


# ── Respuesta de error estándar ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensaje descriptivo del error")
    code: str = Field(..., description="Código de error interno")
