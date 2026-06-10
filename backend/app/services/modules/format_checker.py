"""
FormatChecker: valida que la HU tenga la estructura estándar.

Evalúa:
- Presencia de "Como <usuario>"
- Presencia de "quiero <funcionalidad>"
- Presencia de "para <objetivo>"
- Que las tres partes estén en orden lógico
"""

from app.services.modules.base_module import BaseModule, ModuleResult


class FormatChecker(BaseModule):

    @property
    def name(self) -> str:
        return "Verificador de formato"

    @property
    def weight(self) -> float:
        return 0.20

    @property
    def response_key(self) -> str:
        return "format"

    @property
    def analysis_criteria(self) -> str:
        return """
**format** — Verifica la estructura estándar de la Historia de Usuario:
- Debe contener las tres partes: "Como <usuario>", "quiero <funcionalidad>", "para <objetivo>"
- Las partes deben aparecer en ese orden
- Cada parte debe estar completa (no vacía ni truncada)
- Se permiten variaciones menores de redacción ("Como un", "Quiero poder", etc.)
Penaliza fuertemente si falta alguna de las tres partes.
Penaliza moderadamente si el orden no es el correcto.
"""

    def parse_response(self, module_data: dict) -> ModuleResult:
        return self._safe_parse(module_data)
