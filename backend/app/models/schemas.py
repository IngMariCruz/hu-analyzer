from pydantic import BaseModel, Field


# ── Resultado por Historia de Usuario ──────────────────────────────────────

class HUResult(BaseModel):
    hu_id: str = Field(
        ...,
        description="Identificador de la HU extraído del documento (ej: HU-01)",
        examples=["HU-01"],
    )
    original_text: str = Field(
        ...,
        description="Texto original de la HU tal como aparece en el archivo",
        examples=["Como cliente quiero ver el historial de compras para revisar mis pedidos anteriores."],
    )
    score: int = Field(
        ...,
        ge=1,
        le=100,
        description="Calificación de 1 a 100 basada en formato, claridad y criterios INVEST",
        examples=[75],
    )
    band: str = Field(
        default="",
        description="Banda de la calificación: Excepcional (90–100), Bueno (70–89), Regular (50–69), Crítico (<50)",
        examples=["Bueno"],
    )
    evaluated: bool = Field(
        default=True,
        description="False si la evaluación de esta HU falló tras los reintentos (status del documento: partial)",
        examples=[True],
    )
    feedback: list[str] = Field(
        default_factory=list,
        description="Observaciones específicas citando fragmentos del texto original",
        examples=[["El usuario 'cliente' es válido y concreto.", "Falta criterio de aceptación para paginación."]],
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Sugerencias concretas y aplicables para mejorar la HU",
        examples=[["Agregar criterio: 'El historial muestra máximo 50 órdenes por página.'"]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "hu_id": "HU-01",
                "original_text": "Como cliente quiero ver el historial de compras para revisar mis pedidos anteriores.",
                "score": 75,
                "band": "Bueno",
                "evaluated": True,
                "feedback": [
                    "El usuario 'cliente' es válido y concreto.",
                    "La funcionalidad es única y está bien delimitada.",
                    "Falta criterio de aceptación para paginación del historial.",
                ],
                "suggestions": [
                    "Agregar criterio: 'El historial muestra máximo 50 órdenes por página con opción de cargar más.'",
                    "Especificar si el historial incluye órdenes canceladas.",
                ],
            }
        }
    }


# ── Resumen del proyecto ────────────────────────────────────────────────────

class ProjectSummary(BaseModel):
    objective: str = Field(
        ...,
        description="Objetivo general del proyecto inferido del conjunto de HU",
        examples=["Desarrollar una plataforma e-commerce que permita a clientes gestionar compras y a administradores controlar el inventario."],
    )
    stakeholders: list[str] = Field(
        default_factory=list,
        description="Actores y usuarios identificados en las HU",
        examples=[["Cliente registrado", "Administrador", "Vendedor"]],
    )
    business_rules: list[str] = Field(
        default_factory=list,
        description="Reglas de negocio detectadas implícita o explícitamente en las HU",
        examples=[["Solo clientes registrados pueden ver el historial.", "El inventario se actualiza en tiempo real al confirmar una compra."]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "objective": "Desarrollar una plataforma e-commerce para gestión de compras y control de inventario.",
                "stakeholders": ["Cliente registrado", "Administrador", "Vendedor"],
                "business_rules": [
                    "Solo clientes registrados pueden ver el historial de compras.",
                    "El stock se descuenta al confirmar el pago.",
                ],
            }
        }
    }


# ── Respuesta completa del análisis ────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    analysis_id: str | None = Field(
        default=None,
        description="Identificador opaco para recuperar el resultado en sesión vía GET /analyze/{analysis_id}",
        examples=["3f0a1c2e-7b9d-4e51-9c0a-1b2c3d4e5f60"],
    )
    status: str = Field(
        default="ok",
        description="Resultado del análisis: 'ok', 'partial', 'no_project' o 'invalid'",
        examples=["ok"],
    )
    message: str | None = Field(
        default=None,
        description="Mensaje para el usuario cuando status no es 'ok' (qué falta o por qué)",
    )
    story_count: int = Field(
        default=0,
        description="Número de Historias de Usuario detectadas en el documento",
        examples=[5],
    )
    hu_results: list[HUResult] = Field(
        default_factory=list,
        description="Análisis individual de cada HU encontrada en el archivo",
    )
    project_summary: ProjectSummary = Field(
        ...,
        description="Información global extraída del conjunto completo de HU",
    )
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Promedio simple de las calificaciones (1–100) de las HU evaluadas (0 si no se analizó)",
        examples=[72.0],
    )
    overall_band: str = Field(
        default="",
        description="Banda del promedio del documento (Excepcional/Bueno/Regular/Crítico)",
        examples=["Bueno"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "analysis_id": "3f0a1c2e-7b9d-4e51-9c0a-1b2c3d4e5f60",
                "status": "ok",
                "story_count": 1,
                "hu_results": [
                    {
                        "hu_id": "HU-01",
                        "original_text": "Como cliente quiero ver el historial de compras para revisar mis pedidos anteriores.",
                        "score": 75,
                        "band": "Bueno",
                        "evaluated": True,
                        "feedback": ["Usuario válido.", "Falta criterio de paginación."],
                        "suggestions": ["Agregar criterio de paginación."],
                    }
                ],
                "project_summary": {
                    "objective": "Plataforma e-commerce para gestión de compras.",
                    "stakeholders": ["Cliente registrado", "Administrador"],
                    "business_rules": ["Solo clientes registrados acceden al historial."],
                },
                "overall_score": 75.0,
                "overall_band": "Bueno",
            }
        }
    }


# ── Auth del panel admin (Epic 3) ───────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str | None = Field(
        default=None,
        description="Usuario del administrador (opcional en modo single-admin por .env)",
    )
    password: str = Field(..., description="Contraseña del administrador")


class AdminRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Usuario del administrador")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")


class AdminExistsResponse(BaseModel):
    registered: bool = Field(..., description="True si ya hay un administrador registrado")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT firmado para el panel admin")
    token_type: str = Field(default="bearer", description="Tipo de token (bearer)")


# ── Respuesta de error estándar ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Mensaje descriptivo del error para mostrar al usuario",
        examples=["El archivo supera el tamaño máximo permitido de 10 MB."],
    )
    code: str = Field(
        ...,
        description="Código interno del error para manejo programático",
        examples=["FILE_TOO_LARGE"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Tipo de archivo no soportado: application/zip. Use .docx, .pdf, .xlsx o .txt",
                "code": "UNSUPPORTED_FILE_TYPE",
            }
        }
    }
