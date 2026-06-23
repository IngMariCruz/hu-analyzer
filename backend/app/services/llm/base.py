"""
LLMProvider: interfaz (puerto) para proveedores de modelos de lenguaje.

Desacopla el orquestador de análisis del proveedor concreto (OpenAI hoy),
permitiendo intercambiarlo por configuración y mockearlo en pruebas.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Contrato mínimo que debe implementar un proveedor LLM."""

    @abstractmethod
    async def complete_structured(
        self,
        *,
        system: str,
        prompt: str,
        schema: type[T],
    ) -> T:
        """Devuelve una respuesta estructurada validada contra `schema`.

        Args:
            system: instrucción de sistema.
            prompt: contenido del usuario.
            schema: modelo Pydantic esperado de la respuesta.

        Returns:
            Instancia de `schema` con la respuesta del modelo.
        """
        ...
