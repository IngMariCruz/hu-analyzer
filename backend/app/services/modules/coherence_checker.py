"""
CoherenceChecker: detecta ambigüedad, contradicciones e inconsistencias en la HU.

Evalúa:
- Términos ambiguos ("rápido", "fácil", "algunos", "varios", "adecuado")
- Contradicciones internas dentro de la misma HU
- Inconsistencias entre la funcionalidad descrita y el objetivo declarado
- Lenguaje técnico innecesario que el usuario no debería conocer
"""

from app.services.modules.base_module import BaseModule, ModuleResult


AMBIGUOUS_TERMS = [
    "rápido", "lento", "fácil", "difícil", "simple", "complejo",
    "algunos", "varios", "muchos", "pocos", "adecuado", "apropiado",
    "eficiente", "óptimo", "mejor", "peor", "grande", "pequeño",
    "pronto", "luego", "después", "a veces", "frecuentemente",
]


class CoherenceChecker(BaseModule):

    @property
    def name(self) -> str:
        return "Verificador de coherencia"

    @property
    def weight(self) -> float:
        return 0.15

    @property
    def response_key(self) -> str:
        return "coherence"

    @property
    def analysis_criteria(self) -> str:
        return f"""
**coherence** — Evalúa la coherencia y claridad de la Historia de Usuario:
- Detecta términos ambiguos o subjetivos que no se pueden medir: {", ".join(AMBIGUOUS_TERMS[:10])}, etc.
- Identifica contradicciones internas (ej: "quiero ver todos los registros para no saturar la pantalla")
- Verifica que la funcionalidad y el objetivo sean coherentes entre sí
- Detecta lenguaje técnico inapropiado para una HU de negocio (endpoints, queries, APIs, etc.)
- Evalúa si la HU es comprensible para alguien sin conocimientos técnicos
Penalizar por cada término ambiguo encontrado.
Penalizar fuertemente si hay contradicciones o lenguaje técnico interno.
"""

    def parse_response(self, module_data: dict) -> ModuleResult:
        return self._safe_parse(module_data)
