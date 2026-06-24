# Epic 1 Context: Motor de análisis de HUs

> Contexto cacheado para implementación de stories del Epic 1. Fuente: PRD, architecture.md, epics.md.

## Objetivo del epic
El usuario anónimo sube un documento de HUs y recibe la evaluación completa por HU (score 1–100 + banda, observaciones, sugerencias) más la inferencia de objetivo/usuarios finales/reglas de negocio, sin que el documento se almacene. Resultado recuperable por `analysis_id` en sesión.

## Decisiones de arquitectura relevantes
- **LLM:** GPT-4o mini (OpenAI) detrás de una interfaz `LLMProvider` (puerto con un método); adaptador OpenAI con `AsyncOpenAI`. Retirar `anthropic`, añadir `openai`. Modelo configurable vía `LLM_MODEL` (default `gpt-4o-mini`).
- **Structured Outputs:** `response_format` con `json_schema` + Pydantic para eliminar JSON malformado en origen. Reintento con backoff solo en 429/5xx/timeout.
- **Escala:** 1–100 con bandas (90–100 Excepcional, 70–89 Bueno, 50–69 Regular, <50 Crítico), normalización y bandas centralizadas en la capa de agregación (Story 1.6). Auditar `*10`/`<=10`/`le=10`.
- **Orquestación híbrida (Story 1.5):** 1 llamada nivel-documento (pertinencia→validez→inferencia) + 1 llamada por HU en paralelo (`asyncio.gather` + semáforo).
- **Privacidad:** documento solo en memoria (`BytesIO`), sin `tempfile`; no loguear contenido/prompt; NFR de minimización (inferencias abstraen, no citan verbatim).
- **Persistencia (Story 1.9):** SQLite vía SQLAlchemy; `analysis`, `story_result`, `business_inference` sin identidad; `analysis_id` opaco.
- **Patrón Strategy:** conservar `BaseModule` + checkers; mutan de "orquestar su llamada" a "puntuar su sección del JSON".

## Estado del código (brownfield)
- `backend/app/services/analyzer.py`: orquestador actual con `anthropic.AsyncAnthropic`, modelo `claude-haiku-4-5`, prompt batch único, extracción JSON por regex (`_extract_json`), score ponderado 1–10 (`_calculate_weighted_score`).
- `backend/app/core/config.py`: `Settings` con `ANTHROPIC_API_KEY`, `FRONTEND_ORIGIN`, `MAX_FILE_SIZE_MB`.
- `backend/app/services/modules/`: `base_module.py` (ABC con `name`, `weight`, `response_key`, `analysis_criteria`, `parse_response`) + checkers (format, invest, coherence, user, functionality).
- `backend/app/models/schemas.py`: Pydantic request/response.
- `backend/requirements.txt`: incluye `anthropic>=0.40.0`.

## Convenciones (CONVENTIONS.md)
- Python: PEP8, snake_case, type hints obligatorios, docstrings Google-style, async/await en llamadas externas.
- Prompts como constantes `PROMPT_*` en el módulo; pedir JSON estructurado.
- Errores API: HTTP 422/500 con `{detail, code}`.

## Stories del epic
1.1 LLMProvider + migración GPT-4o mini · 1.2 ingesta en memoria · 1.3 gate pertinencia/validez · 1.4 segmentación · 1.5 evaluación por HU · 1.6 score/bandas/promedio · 1.7 sugerencias · 1.8 inferencia con minimización · 1.9 persistencia + analysis_id · 1.10 frontend resultados · 1.11 rate-limiting + topes.

## Estado del epic: COMPLETO (1.1 → 1.11)
Stories 1.1–1.11 implementadas. Hitos clave:
- **1.5/1.8** orquestación híbrida en `analyzer.py` (1 llamada por HU bajo semáforo + 1 llamada de inferencia en `inference.py`), `status: partial` ante fallo de una HU.
- **1.6** escala centralizada en `services/scoring.py` (1–100 + bandas); `HUResult.score:int`, `band`, `overall_band`; PDF auditado.
- **1.7** sugerencias solo para HU con score < 90.
- **1.9** persistencia SQLite sin identidad en `app/db/` + `services/persistence.py`; `analysis_id` opaco; `GET /analyze/{id}`; `original_text` nunca persistido.
- **1.10** frontend ramifica por status (alerta/replantear/partial/resultados) en escala 1–100 con reintento.
- **1.11** rate-limit efímero (slowapi por IP, `app/core/ratelimit.py`) + topes de archivo antes del LLM.

Specs por story en `_bmad-output/implementation-artifacts/spec-1-*.md`. Tests: `pytest` en `backend/` (22 verdes). Siguiente epic: Epic 2 (reportes PDF desde el resultado persistido) — nota: el PDF actual se genera desde el `AnalyzeResponse` recibido; 2.1 pedirá generarlo desde el resultado persistido por `analysis_id` con builder común.
