"""
BaseModule: clase abstracta que deben implementar todos los módulos de análisis.

Patrón Strategy — cada módulo encapsula un criterio de evaluación independiente.
Para agregar un nuevo módulo: crear archivo en services/modules/, heredar BaseModule,
registrarlo en analyzer.py. No se toca ningún otro archivo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ModuleResult:
    """Resultado de un módulo de análisis individual."""
    module_name: str
    score: float                          # 0.0 – 10.0
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    weight: float = 1.0                   # Peso para el promedio ponderado final


class BaseModule(ABC):
    """
    Clase base para todos los módulos de análisis de HU.

    Cada módulo define:
    - name: identificador legible
    - weight: cuánto pesa en la calificación final
    - analysis_criteria: descripción de lo que evalúa (usado en el prompt compuesto)
    - response_key: clave en el JSON de Claude para este módulo
    - parse_response: extrae un ModuleResult desde la respuesta de Claude

    El Analyzer (services/analyzer.py) compone un único prompt con todos los
    módulos activos y distribuye la respuesta a cada uno para parsear.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre legible del módulo (ej: 'Verificador de formato')."""
        ...

    @property
    @abstractmethod
    def weight(self) -> float:
        """Peso del módulo en la calificación final (todos deben sumar 1.0)."""
        ...

    @property
    @abstractmethod
    def response_key(self) -> str:
        """Clave en el JSON de respuesta de Claude para este módulo (ej: 'format')."""
        ...

    @property
    @abstractmethod
    def analysis_criteria(self) -> str:
        """
        Descripción detallada de los criterios que este módulo evalúa.
        Se inserta dentro del prompt compuesto que se envía a Claude.
        """
        ...

    @abstractmethod
    def parse_response(self, module_data: dict) -> ModuleResult:
        """
        Parsea la sección de este módulo desde la respuesta JSON de Claude.

        Args:
            module_data: diccionario con las claves 'score', 'issues', 'suggestions'
                         tal como las retornó Claude para este módulo.

        Returns:
            ModuleResult con score, issues y suggestions del módulo.
        """
        ...

    def _safe_parse(self, module_data: dict) -> ModuleResult:
        """
        Implementación segura de parse_response con manejo de claves faltantes.
        Los módulos concretos pueden llamar a este método o sobreescribir parse_response.
        """
        return ModuleResult(
            module_name=self.name,
            score=float(module_data.get("score", 5.0)),
            issues=module_data.get("issues", []),
            suggestions=module_data.get("suggestions", []),
            weight=self.weight,
        )
