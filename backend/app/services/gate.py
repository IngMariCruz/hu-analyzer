"""
Gate de pertinencia y validez del documento (Story 1.3).

Llamada LLM a nivel documento que decide, antes de analizar las HU:
- `no_project`: el documento no contiene información de un proyecto.
- `invalid`: contiene un proyecto pero la información no permite entender el core
  del negocio (en `message` se indica qué falta).
- `ok`: la información es suficiente; se procede con el análisis.
"""

import logging

from app.services.llm import LLMProvider, get_llm_provider
from app.services.llm.schemas import GateResult

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Eres un analista de requisitos de software. Clasificas si un documento "
    "contiene la información de un proyecto descrito mediante Historias de "
    "Usuario o requisitos, y si esa información es suficiente para analizarla."
)


def _build_prompt(raw_text: str) -> str:
    return f"""Clasifica el siguiente documento en uno de estos estados:

- "no_project": NO contiene información de un proyecto de software (texto
  irrelevante, sin requisitos ni historias de usuario, otro tema).
- "invalid": contiene un proyecto pero la información NO es suficiente para
  entender el core del negocio (falta objetivo, historias sin contexto,
  demasiado ambiguo o incompleto).
- "ok": contiene un proyecto y la información es suficiente para analizar.

En `message`, escribe una explicación breve y útil para el usuario: si es
"invalid" indica QUÉ falta o debe replantear; si es "no_project" explica por
qué; si es "ok" resume de qué trata el proyecto.

## Documento

{raw_text}
"""


async def check_document(
    raw_text: str,
    provider: LLMProvider | None = None,
) -> GateResult:
    """Clasifica la pertinencia/validez del documento.

    Args:
        raw_text: texto completo extraído del documento.
        provider: proveedor LLM a usar; por defecto el configurado.

    Returns:
        GateResult con el estado y un mensaje para el usuario.
    """
    provider = provider or get_llm_provider()
    logger.info("Ejecutando gate de pertinencia/validez del documento.")
    return await provider.complete_structured(
        system=_SYSTEM_PROMPT,
        prompt=_build_prompt(raw_text),
        schema=GateResult,
    )
