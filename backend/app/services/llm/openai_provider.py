"""
OpenAIProvider: adaptador de LLMProvider sobre la API de OpenAI.

Usa Structured Outputs (`response_format` con un modelo Pydantic) para obtener
JSON válido por construcción, y delega los reintentos en el SDK (`max_retries`).
"""

import logging
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    """Proveedor LLM respaldado por OpenAI (GPT-4o mini por defecto)."""

    def __init__(self, api_key: str, model: str, max_retries: int = 2) -> None:
        self._client = AsyncOpenAI(api_key=api_key, max_retries=max_retries)
        self._model = model

    async def complete_structured(
        self,
        *,
        system: str,
        prompt: str,
        schema: type[T],
    ) -> T:
        completion = await self._client.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            response_format=schema,
        )

        usage = completion.usage
        if usage is not None:
            # Solo metadatos: nunca se loguea el contenido del documento ni el prompt.
            logger.info("LLM tokens usados — total: %s", usage.total_tokens)

        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("El proveedor LLM no devolvió contenido estructurado.")
        return parsed
