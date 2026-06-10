"""
UserChecker: valida que el actor de la HU sea un usuario real del negocio.

Evalúa:
- Que el usuario NO sea QA, tester, desarrollador, equipo técnico o el sistema mismo
- Que el usuario sea concreto (no "usuario genérico" o "alguien")
- Que el usuario tenga un rol de negocio reconocible
"""

from app.services.modules.base_module import BaseModule, ModuleResult


INVALID_USERS = [
    "qa", "tester", "desarrollador", "developer", "equipo de desarrollo",
    "equipo técnico", "analista", "scrum master", "product owner",
    "el sistema", "la aplicación", "el software", "admin técnico",
]


class UserChecker(BaseModule):

    @property
    def name(self) -> str:
        return "Verificador de usuario"

    @property
    def weight(self) -> float:
        return 0.20

    @property
    def response_key(self) -> str:
        return "user"

    @property
    def analysis_criteria(self) -> str:
        return f"""
**user** — Verifica que el actor de la Historia de Usuario sea válido:
- El usuario NO debe ser un rol técnico: {", ".join(INVALID_USERS)}
- El usuario debe ser un actor del negocio o usuario final del sistema
- El usuario debe ser concreto y específico (evitar "usuario" genérico sin contexto)
- Se acepta "administrador" solo si es un rol de negocio (no técnico)
Penaliza fuertemente si el usuario es un rol técnico o de QA.
Penaliza moderadamente si el usuario es demasiado genérico o vago.
"""

    def parse_response(self, module_data: dict) -> ModuleResult:
        return self._safe_parse(module_data)
