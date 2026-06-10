"""
Registro de módulos de análisis activos.

Para agregar un nuevo módulo:
1. Crear el archivo en este directorio heredando BaseModule
2. Importarlo aquí y agregarlo a ACTIVE_MODULES
No se necesita modificar ningún otro archivo.
"""

from app.services.modules.format_checker import FormatChecker
from app.services.modules.user_checker import UserChecker
from app.services.modules.functionality_checker import FunctionalityChecker
from app.services.modules.invest_checker import InvestChecker
from app.services.modules.coherence_checker import CoherenceChecker
from app.services.modules.base_module import BaseModule

ACTIVE_MODULES: list[BaseModule] = [
    FormatChecker(),
    UserChecker(),
    FunctionalityChecker(),
    InvestChecker(),
    CoherenceChecker(),
]

__all__ = ["ACTIVE_MODULES", "BaseModule"]
