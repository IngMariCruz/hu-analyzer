"""
Inferencia de negocio (Story 1.8).

Llamada LLM nivel-documento que infiere objetivo del proyecto, usuarios finales
y reglas de negocio. Aplica la NFR de minimización: las inferencias deben
ABSTRAER, no citar verbatim; sin nombres propios ni identificadores. Lo que aquí
se produce es lo único que se persiste como "negocio" del documento.
"""

import logging

from app.services.file_parser import ParsedHU
from app.services.llm import LLMProvider, get_llm_provider
from app.services.llm.schemas import BusinessInferenceResponse

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Eres un analista de negocio. A partir de un conjunto de Historias de "
    "Usuario infieres el negocio que hay detrás. REGLA ESTRICTA DE "
    "MINIMIZACIÓN: abstrae, no cites; está prohibido incluir nombres propios, "
    "nombres de personas o empresas, identificadores, rutas, o fragmentos "
    "textuales (verbatim) del documento. Describe en términos genéricos."
)


def _build_prompt(parsed_hus: list[ParsedHU]) -> str:
    hus_section = "\n\n".join(f"### {hu.hu_id}\n{hu.raw_text}" for hu in parsed_hus)
    return f"""A partir de las siguientes Historias de Usuario infiere:

- `objective`: el objetivo general del proyecto, en una o dos frases abstractas.
- `end_users`: SOLO los usuarios finales del producto (no equipos técnicos, no
  QA, no desarrolladores). Roles genéricos, sin nombres propios.
- `business_rules`: las reglas de negocio implícitas o explícitas, redactadas de
  forma abstracta.

NO copies frases del documento ni incluyas nombres propios, identificadores o
datos concretos. Si algo no se puede inferir, deja la lista vacía o una frase
breve indicándolo en `objective`.

## Historias de Usuario

{hus_section}
"""


async def infer_business(
    parsed_hus: list[ParsedHU],
    provider: LLMProvider | None = None,
) -> BusinessInferenceResponse:
    """Infiere objetivo, usuarios finales y reglas de negocio (abstraídos).

    Args:
        parsed_hus: HU segmentadas del documento.
        provider: proveedor LLM a usar; por defecto el configurado.

    Returns:
        BusinessInferenceResponse con las inferencias minimizadas.
    """
    provider = provider or get_llm_provider()
    logger.info("Ejecutando inferencia de negocio nivel-documento.")
    return await provider.complete_structured(
        system=_SYSTEM_PROMPT,
        prompt=_build_prompt(parsed_hus),
        schema=BusinessInferenceResponse,
    )
