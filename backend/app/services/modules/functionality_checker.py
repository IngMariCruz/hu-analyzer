"""
FunctionalityChecker: valida que la HU describa una sola funcionalidad con objetivo claro.

Evalúa:
- Que la funcionalidad sea única (no "quiero X y también Y")
- Que el objetivo ("para...") sea claro y medible
- Que no haya múltiples verbos de acción en la parte "quiero"
"""

from app.services.modules.base_module import BaseModule, ModuleResult


class FunctionalityChecker(BaseModule):

    @property
    def name(self) -> str:
        return "Verificador de funcionalidad única"

    @property
    def weight(self) -> float:
        return 0.20

    @property
    def response_key(self) -> str:
        return "functionality"

    @property
    def analysis_criteria(self) -> str:
        return """
**functionality** — Verifica que la HU cubra exactamente una funcionalidad:
- La parte "quiero" debe describir UNA sola acción o capacidad
- No debe contener conectores que unan múltiples funcionalidades ("y", "además", "también", "así como")
- El objetivo ("para") debe ser claro, específico y verificable
- El objetivo no debe ser vago ("para mejorar la experiencia", "para que sea mejor")
Penaliza fuertemente si hay más de una funcionalidad descrita.
Penaliza moderadamente si el objetivo es vago o inmesurable.
"""

    def parse_response(self, module_data: dict) -> ModuleResult:
        return self._safe_parse(module_data)
