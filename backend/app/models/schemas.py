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
    score: float = Field(
        ...,
        ge=1.0,
        le=10.0,
        description="Calificación de 1.0 a 10.0 basada en formato, claridad y criterios INVEST",
        examples=[7.5],
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
                "score": 7.5,
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
        ge=1.0,
        le=10.0,
        description="Promedio ponderado de las calificaciones de todas las HU",
        examples=[7.2],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "hu_results": [
                    {
                        "hu_id": "HU-01",
                        "original_text": "Como cliente quiero ver el historial de compras para revisar mis pedidos anteriores.",
                        "score": 7.5,
                        "feedback": ["Usuario válido.", "Falta criterio de paginación."],
                        "suggestions": ["Agregar criterio de paginación."],
                    }
                ],
                "project_summary": {
                    "objective": "Plataforma e-commerce para gestión de compras.",
                    "stakeholders": ["Cliente registrado", "Administrador"],
                    "business_rules": ["Solo clientes registrados acceden al historial."],
                },
                "overall_score": 7.5,
            }
        }
    }


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
