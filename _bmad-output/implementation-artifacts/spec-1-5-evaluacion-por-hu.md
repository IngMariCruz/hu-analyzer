---
title: 'Story 1.5 — Evaluación por HU (orquestación híbrida)'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Migrar del prompt batch único a orquestación híbrida: 1 llamada por HU en paralelo (`asyncio.gather` + `asyncio.Semaphore`) para su evaluación (formato, INVEST, coherencia/ambigüedad) + 1 llamada nivel-documento para la inferencia. Si una HU falla tras los reintentos del SDK, se marca sin abortar el resto (`status: partial`).

## Resultado
`analyzer.analyze` reescrito: `_evaluate_hu` corre bajo semáforo (`LLM_MAX_CONCURRENCY`, default 5) y captura excepciones devolviendo `None` → HU con `evaluated=False`. Esquema por-HU `HUEvaluationResponse(modules)` y `_build_hu_result` mapea + puntúa vía `scoring.py`. La evaluación por-HU y la inferencia se lanzan concurrentes con `asyncio.gather`. El backoff en 429/5xx/timeout lo aporta `OpenAIProvider` (SDK `max_retries`). Los checkers Strategy siguen aportando `analysis_criteria`/`response_key` (puntúan su sección, no orquestan).

## Cubre
FR11, FR12, FR13, FR14 (ambigüedad por-HU; contradicción cross-documento queda aproximada por coherencia + inferencia).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_analyzer.py -q` -- expected: verde (incluye `status: partial` al fallar una HU).
