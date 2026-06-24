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
- **Verbos HTTP:** POST para análisis/login; GET para recuperar resultado, reportes y métricas.
- **Respuestas exitosas:** HTTP 200 (JSON `AnalyzeResponse` o `application/pdf` en reportes).
- **Errores:** 422 (tipo no soportado/validación), 413 (tamaño), 429 (rate-limit), 401 (admin sin/JWT inválido), 404 (`analysis_id` inexistente), 500 (interno) — siempre con mensaje descriptivo.
- **Auth admin:** `Authorization: Bearer <JWT>` en `/api/v1/admin/*` (excepto `login`).

```json
// Estructura de error estándar
{
  "detail": "El archivo supera el tamaño máximo permitido (10 MB)",
  "code": "FILE_TOO_LARGE"
}
```

---

## Módulos de análisis (Strategy)

- Cada módulo vive en `services/modules/`, hereda de `BaseModule` y es stateless.
- Aporta `name`, `weight`, `response_key`, `analysis_criteria` y `parse_response(module_data)`.
- **No** orquesta su propia llamada al LLM: interpreta y puntúa su sección del JSON estructurado.
- Se registran en `services/modules/__init__.py` (`ACTIVE_MODULES`).
- El score 1–100 y las bandas se calculan en `services/scoring.py` (no en el checker).

---

## Manejo de prompts al LLM (OpenAI GPT-4o mini vía `LLMProvider`)

- Los prompts viven como constantes `_SYSTEM_PROMPT` / funciones `_build_*_prompt` en el módulo correspondiente.
- Usar **Structured Outputs**: `provider.complete_structured(system, prompt, schema=ModeloPydantic)` — el JSON es válido por construcción (no pedir "responde SOLO con JSON").
- Los esquemas de respuesta viven en `services/llm/schemas.py` (Pydantic, listas estáticas, compatibles con el modo estricto de OpenAI).
- **Nunca** loguear el contenido del documento ni el prompt (solo metadatos: tipo, tamaño, duración, tokens).
- Minimización: los prompts de inferencia prohíben verbatim, nombres propios e identificadores.

```python
data = await provider.complete_structured(
    system=_SYSTEM_PROMPT,
    prompt=_build_hu_prompt(hu),
    schema=HUEvaluationResponse,   # { modules: [{ key, score, issues, suggestions }] }
)
```

---

## Git

- **Ramas:** `main` (estable), `dev` (desarrollo), `feature/nombre-corto`
- **Commits:** en español, imperativo: "Agrega validación de formato HU"
- **No subir:** `.env`, `node_modules/`, `__pycache__/`, `*.pyc`
