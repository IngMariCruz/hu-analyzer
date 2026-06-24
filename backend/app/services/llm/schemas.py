"""
Esquemas Pydantic de las respuestas estructuradas del proveedor LLM.

Se usan como `response_format` (Structured Outputs) para garantizar JSON válido.
La orquestación es híbrida (Story 1.5): una llamada nivel-documento para el gate
y la inferencia de negocio, y una llamada por HU para su evaluación. Las listas
de módulos son estáticas (sin claves dinámicas) para ser compatibles con los
esquemas estrictos de OpenAI.
"""

from typing import Literal

from pydantic import BaseModel


class GateResult(BaseModel):
    """Clasificación de pertinencia/validez del documento (gate previo al análisis)."""
    status: Literal["ok", "no_project", "invalid"]
    message: str


class ModuleEvaluation(BaseModel):
    """Evaluación de un criterio (módulo) para una HU."""
    key: str
    score: float
    issues: list[str]
    suggestions: list[str]


class HUEvaluationResponse(BaseModel):
    """Respuesta estructurada de la evaluación de UNA HU (1 llamada por HU)."""
    modules: list[ModuleEvaluation]


class BusinessInferenceResponse(BaseModel):
    """Inferencia de negocio nivel-documento, abstraída (NFR de minimización)."""
    objective: str
    end_users: list[str]
    business_rules: list[str]
