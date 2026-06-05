# HU Analyzer — Convenciones de Código

> Pegar en sesiones donde se esté escribiendo código.

---

## Python (Backend)

- **Estilo:** PEP8, nombres en `snake_case`
- **Clases:** `PascalCase`
- **Constantes:** `UPPER_SNAKE_CASE`
- **Type hints:** obligatorios en funciones públicas
- **Docstrings:** en clases y métodos públicos, formato Google-style
- **Async:** usar `async/await` en endpoints y llamadas a API externa

```python
# ✅ Correcto
async def analyze_hu(hu_text: str) -> HUResult:
    """Analiza una HU individual y retorna calificación y retroalimentación."""
    ...

# ❌ Incorrecto
def analyzeHU(text):
    ...
```

---

## React (Frontend)

- **Componentes:** `PascalCase`, un componente por archivo
- **Variables/funciones:** `camelCase`
- **Hooks:** siempre al inicio del componente
- **Props:** destructuradas en la firma de la función
- **No usar:** `class components`, `var`

```jsx
// ✅ Correcto
function ResultCard({ huId, score, feedback }) {
  const [expanded, setExpanded] = useState(false);
  ...
}

// ❌ Incorrecto
class ResultCard extends Component { ... }
```

---

## API REST

- **Versionado:** `/api/v1/...`
- **Verbos HTTP:** POST para análisis con archivo
- **Respuestas exitosas:** HTTP 200 con `AnalyzeResponse`
- **Errores:** HTTP 422 (validación), 500 (error interno), siempre con mensaje descriptivo

```json
// Estructura de error estándar
{
  "detail": "El archivo supera el tamaño máximo permitido (10 MB)",
  "code": "FILE_TOO_LARGE"
}
```

---

## Módulos de análisis

- Cada módulo vive en `services/modules/`
- Hereda de `BaseModule`
- Implementa SOLO el método `analyze(hu_text: str) -> ModuleResult`
- No tienen estado (stateless)
- No llaman a la API directamente: reciben el contexto del `Analyzer`

---

## Manejo de prompts a Claude

- Los prompts viven en el archivo del módulo correspondiente como constantes
- Se nombran: `PROMPT_NOMBRE_MODULO`
- Siempre pedir respuesta en JSON estructurado
- Incluir instrucción: "Responde SOLO con JSON, sin markdown ni texto adicional"

```python
PROMPT_FORMAT_CHECKER = """
Eres un experto en metodologías ágiles. Analiza la siguiente Historia de Usuario...
Responde SOLO con un JSON con esta estructura exacta:
{ "score": 0-10, "issues": [...], "suggestions": [...] }
"""
```

---

## Git

- **Ramas:** `main` (estable), `dev` (desarrollo), `feature/nombre-corto`
- **Commits:** en español, imperativo: "Agrega validación de formato HU"
- **No subir:** `.env`, `node_modules/`, `__pycache__/`, `*.pyc`
