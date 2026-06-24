---
title: 'Story 1.1 — Abstracción LLMProvider y migración a GPT-4o mini'
type: 'refactor'
created: '2026-06-23'
status: 'done'
baseline_commit: '028e9cb05d0fce3b0feefca4403b6544b6884505'
context:
  - '{project-root}/CONVENTIONS.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** El análisis está acoplado a la API de Anthropic/Claude (`analyzer.py` y el route lo importan directamente) con extracción de JSON por regex frágil. La v1 debe usar OpenAI GPT-4o mini y un proveedor intercambiable.

**Approach:** Introducir una interfaz `LLMProvider` con un adaptador OpenAI (`AsyncOpenAI`) que use Structured Outputs (`json_schema` + Pydantic). Reemplazar la integración Anthropic detrás de esa interfaz, preservando el comportamiento batch actual y la escala 0–10. Modelo configurable vía `LLM_MODEL`.

## Boundaries & Constraints

**Always:** Preservar el contrato actual de `analyze()` (devuelve `AnalyzeResponse` con la misma escala 0–10 y promedio ponderado existente). Usar `async/await`, type hints y docstrings Google-style (CONVENTIONS.md). El proveedor debe ser inyectable para test. Loguear solo metadatos (tokens, conteo), nunca el contenido del documento ni el prompt.

**Ask First:** Cambiar la forma del JSON de respuesta del LLM más allá de lo necesario para Structured Outputs; tocar la lógica de scoring/bandas (es Story 1.6).

**Never:** Cambiar la escala a 1–100, añadir el gate de pertinencia/validez, ni la orquestación por-HU (son stories 1.3/1.5/1.6). No persistir nada. No modificar los checkers Strategy ni `base_module.py`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Lista de `ParsedHU` válida | `AnalyzeResponse` con score por HU (0–10), feedback, sugerencias y `project_summary` | N/A |
| Lista vacía | `parsed_hus == []` | Lanza `ValueError` (igual que hoy) | Propaga a 422 en el route |
| Auth inválida | API key OpenAI inválida | Excepción `openai.AuthenticationError` | Route → 500 mensaje claro |
| Rate limit | OpenAI 429 | `openai.RateLimitError` tras reintentos del SDK | Route → 429 mensaje claro |
| Error de API | OpenAI 5xx/timeout | `openai.APIError` tras `max_retries` | Route → 500 mensaje claro |

</frozen-after-approval>

## Code Map

- `backend/app/services/llm/__init__.py` -- NUEVO: expone `LLMProvider` y `get_llm_provider()` (singleton configurado).
- `backend/app/services/llm/base.py` -- NUEVO: ABC `LLMProvider` con `complete_structured(system, prompt, schema)`.
- `backend/app/services/llm/openai_provider.py` -- NUEVO: `OpenAIProvider` con `AsyncOpenAI` (max_retries), `beta.chat.completions.parse`, log de `usage.total_tokens`.
- `backend/app/services/llm/schemas.py` -- NUEVO: modelos Pydantic de la respuesta estructurada (`AnalysisLLMResponse`, `HUEvaluation`, `ModuleEvaluation`, `ProjectSummarySchema`).
- `backend/app/services/analyzer.py` -- reemplazar Anthropic por `LLMProvider`; `analyze(parsed_hus, provider=None)` usa `get_llm_provider()` por defecto; nuevo prompt que pide `modules: [{key,...}]`; mapear lista→dict por `response_key`; eliminar `_extract_json`; conservar `_calculate_weighted_score`.
- `backend/app/core/config.py` -- `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`; añadir `LLM_MODEL: str = "gpt-4o-mini"`.
- `backend/app/api/v1/routes/analyze.py` -- `import anthropic` → `import openai`; mapear `anthropic.*Error` → `openai.AuthenticationError|RateLimitError|APIError`.
- `backend/requirements.txt` -- quitar `anthropic`, añadir `openai`.
- `backend/.env.example` -- `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`; añadir `LLM_MODEL`.
- `backend/tests/test_analyzer.py` -- NUEVO: test con `LLMProvider` falso.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/llm/schemas.py` -- definir modelos Pydantic de respuesta estructurada (lista estática de módulos por HU, sin claves dinámicas) -- compatible con Structured Outputs estrictos.
- [x] `backend/app/services/llm/base.py` -- ABC `LLMProvider.complete_structured` genérico sobre el modelo Pydantic de salida.
- [x] `backend/app/services/llm/openai_provider.py` -- adaptador OpenAI con `AsyncOpenAI(api_key, max_retries=2)` y `.beta.chat.completions.parse(model, messages, response_format=schema)`; log de tokens (metadato).
- [x] `backend/app/services/llm/__init__.py` -- `get_llm_provider()` devuelve `OpenAIProvider` con `settings.OPENAI_API_KEY` y `settings.LLM_MODEL`.
- [x] `backend/app/core/config.py` -- swap de clave + `LLM_MODEL`.
- [x] `backend/app/services/analyzer.py` -- usar el proveedor, nuevo prompt/mapeo, quitar Anthropic y `_extract_json`.
- [x] `backend/app/api/v1/routes/analyze.py` -- mapear excepciones a `openai.*`.
- [x] `backend/requirements.txt` + `backend/.env.example` -- swap de dependencia y variables.
- [x] `backend/tests/test_analyzer.py` -- proveedor falso que devuelve un `AnalysisLLMResponse` fijo; verifica que `analyze()` produce `AnalyzeResponse` con scores y `project_summary` correctos; caso lista vacía → `ValueError`.

**Acceptance Criteria:**
- Given un `LLMProvider` falso inyectado, when se llama `analyze(parsed_hus, provider=fake)`, then se obtiene `AnalyzeResponse` con un `HUResult` por HU y el `project_summary` poblado, sin tocar red.
- Given el código migrado, when se busca `anthropic` en `backend/`, then no hay ninguna referencia y `requirements.txt` lista `openai`.
- Given `LLM_MODEL` sin definir, when arranca la app, then usa `gpt-4o-mini` por defecto.

## Verification

**Commands:**
- `cd backend && python -m pytest tests/test_analyzer.py -q` -- expected: tests en verde.
- `cd backend && python -c "import app.services.analyzer, app.api.v1.routes.analyze"` -- expected: import sin error (sin `anthropic`).
- `cd backend && grep -rin anthropic app/ requirements.txt` -- expected: sin coincidencias.

## Suggested Review Order

**Diseño del proveedor (entry point)**

- Contrato del puerto: define qué espera el orquestador de cualquier LLM.
  [`base.py:20`](../../backend/app/services/llm/base.py#L20)

- Adaptador OpenAI: Structured Outputs vía `chat.completions.parse`, reintentos del SDK, log solo de tokens.
  [`openai_provider.py:35`](../../backend/app/services/llm/openai_provider.py#L35)

- Fábrica del proveedor configurado (modelo desde settings).
  [`__init__.py:16`](../../backend/app/services/llm/__init__.py#L16)

**Orquestación (cambio central)**

- `analyze()` ahora recibe un proveedor inyectable y usa salida estructurada.
  [`analyzer.py:65`](../../backend/app/services/analyzer.py#L65)

- Llamada estructurada que reemplaza la extracción de JSON por regex.
  [`analyzer.py:88`](../../backend/app/services/analyzer.py#L88)

**Esquema estructurado**

- Respuesta con lista estática de módulos por HU (compatible con esquemas estrictos).
  [`schemas.py:33`](../../backend/app/services/llm/schemas.py#L33)

**Configuración y errores**

- Swap de clave + modelo configurable (default gpt-4o-mini).
  [`config.py:5`](../../backend/app/core/config.py#L5)

- Mapeo de excepciones Anthropic→OpenAI en el endpoint.
  [`analyze.py:121`](../../backend/app/api/v1/routes/analyze.py#L121)

**Periféricos**

- Test del orquestador con proveedor falso (sin red).
  [`test_analyzer.py:1`](../../backend/tests/test_analyzer.py#L1)

- Dependencias: quita `anthropic`, añade `openai`.
  [`requirements.txt:6`](../../backend/requirements.txt#L6)
