"""
Esquemas Pydantic de la respuesta estructurada del proveedor LLM.

Se usan como `response_format` (Structured Outputs) para garantizar JSON válido.
La lista de módulos por HU es estática (sin claves dinámicas) para ser
compatible con los esquemas estrictos de OpenAI.
"""

from pydantic import BaseModel


class ModuleEvaluation(BaseModel):
    """Evaluación de un criterio (módulo) para una HU."""
    key: str
    score: float
    issues: list[str]
    suggestions: list[str]


class HUEvaluation(BaseModel):
    """Evaluación completa de una HU con todos sus módulos."""
    hu_id: str
    modules: list[ModuleEvaluation]


class ProjectSummarySchema(BaseModel):
    """Información global inferida del conjunto de HU."""
    objective: str
    stakeholders: list[str]
    business_rules: list[str]


class AnalysisLLMResponse(BaseModel):
    """Respuesta estructurada completa del análisis."""
    hu_results: list[HUEvaluation]
    project_summary: ProjectSummarySchema
