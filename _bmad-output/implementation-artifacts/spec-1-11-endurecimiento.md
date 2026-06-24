---
title: 'Story 1.11 — Endurecimiento: rate-limiting efímero y topes de archivo'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Limitar el abuso anónimo sin almacenar identidad: rate-limit por IP (solo en memoria, nunca persistida) y topes de tamaño/tipo de archivo aplicados antes de invocar el LLM.

## Resultado
Nuevo `app/core/ratelimit.py` con `Limiter(key_func=get_remote_address)` (slowapi, contadores en memoria). `POST /analyze` decorado con `@limiter.limit(settings.RATE_LIMIT)` (default `10/minute`); `main.py` monta `app.state.limiter` + handler de `RateLimitExceeded`. La IP nunca llega a la base (el modelo de datos no tiene columna de IP). Los topes de tipo (`ALLOWED_CONTENT_TYPES` → 422) y tamaño (`MAX_FILE_SIZE_MB` → 413) ya se evaluaban antes de parsear/llamar al LLM y se conservan. Dependencias: `slowapi`.

## Cubre
FR3 (rechazo previo) + NFR5/NFR8 (topes y rate-limit sin persistir identidad).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_route.py -q` -- expected: verde (422 tipo no soportado, 413 sobre-tamaño, limiter montado, 404 recuperación).
