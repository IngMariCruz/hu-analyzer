"""
Pruebas del gate de pertinencia/validez (Story 1.3) con proveedor falso.
"""

import asyncio

from app.services.gate import check_document
from app.services.llm.base import LLMProvider
from app.services.llm.schemas import GateResult


class FakeProvider(LLMProvider):
    def __init__(self, result: GateResult) -> None:
        self._result = result

    async def complete_structured(self, *, system, prompt, schema):
        return self._result


def test_gate_ok():
    result = asyncio.run(
        check_document("Un proyecto de e-commerce...", provider=FakeProvider(
            GateResult(status="ok", message="Proyecto de e-commerce."),
        ))
    )
    assert result.status == "ok"


def test_gate_no_project():
    result = asyncio.run(
        check_document("Receta de cocina.", provider=FakeProvider(
            GateResult(status="no_project", message="No es un proyecto."),
        ))
    )
    assert result.status == "no_project"
    assert result.message


def test_gate_invalid():
    result = asyncio.run(
        check_document("Texto ambiguo.", provider=FakeProvider(
            GateResult(status="invalid", message="Falta el objetivo del proyecto."),
        ))
    )
    assert result.status == "invalid"
    assert "objetivo" in result.message.lower()
