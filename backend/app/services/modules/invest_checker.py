"""
InvestChecker: evalúa los criterios de aceptación bajo el principio INVEST.

INVEST:
- Independent  → la HU es independiente de otras
- Negotiable   → no es un contrato rígido, deja espacio al diálogo
- Valuable     → aporta valor real al usuario o negocio
- Estimable    → se puede estimar el esfuerzo
- Small        → tiene un tamaño manejable para un sprint
- Testable     → se puede verificar si está cumplida
"""

from app.services.modules.base_module import BaseModule, ModuleResult


class InvestChecker(BaseModule):

    @property
    def name(self) -> str:
        return "Verificador INVEST"

    @property
    def weight(self) -> float:
        return 0.25

    @property
    def response_key(self) -> str:
        return "invest"

    @property
    def analysis_criteria(self) -> str:
        return """
**invest** — Evalúa los criterios de aceptación de la HU bajo el principio INVEST:
- **I (Independent):** ¿La HU puede desarrollarse sin depender de otra HU específica?
- **N (Negotiable):** ¿Los criterios dejan espacio para decisiones de implementación?
- **V (Valuable):** ¿La HU aporta valor claro y directo al usuario o al negocio?
- **E (Estimable):** ¿Es posible estimar el esfuerzo de desarrollo con la información dada?
- **S (Small):** ¿La HU es lo suficientemente pequeña para completarse en un sprint?
- **T (Testable):** ¿Los criterios de aceptación permiten verificar si la HU está cumplida?

Si la HU no tiene criterios de aceptación explícitos, penalizar fuertemente T y E.
Evaluar cada letra por separado e identificar cuáles fallan.
"""

    def parse_response(self, module_data: dict) -> ModuleResult:
        return self._safe_parse(module_data)
