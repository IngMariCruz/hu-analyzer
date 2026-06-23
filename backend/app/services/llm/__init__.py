"""
Paquete de proveedores LLM.

Expone la interfaz `LLMProvider` y una fábrica `get_llm_provider()` que
construye el proveedor configurado (OpenAI por defecto).
"""

from functools import lru_cache

from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Devuelve el proveedor LLM configurado (singleton)."""
    return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.LLM_MODEL)


__all__ = ["LLMProvider", "OpenAIProvider", "get_llm_provider"]
