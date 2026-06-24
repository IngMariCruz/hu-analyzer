---
title: 'Story 1.9 — Persistencia del resultado y recuperación por analysis_id'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Persistir el resultado en SQLite (SQLAlchemy) SIN documento, texto extraído ni PII; devolver `analysis_id` opaco; recuperar vía `GET /api/v1/analyze/{analysis_id}`. El registro es también el evento de uso (FR28).

## Resultado
Nuevo paquete `app/db/` (`models.py`, `session.py`) con modelos sin identidad: `analysis` (id UUID, created_at, status, story_count, overall_score, duration_ms, model_version, file_type), `story_result` (score 1–100, evaluated, feedback/suggestions JSON — **sin `original_text`**) y `business_inference` (objective, end_users, business_rules JSON). `app/services/persistence.py` con `save_analysis`/`load_analysis`; al recuperar, `original_text` se devuelve vacío y las bandas se recalculan. El route `POST /analyze` persiste en todas las rutas (incl. gate `no_project`/`invalid`/sin-HU) y setea `result.analysis_id`. `init_db()` en el `lifespan` de FastAPI. Bandas calculadas en lectura, no almacenadas. `*.db` ignorado en git.

## Cubre
FR28 (+ FR4/NFR1 privacidad: el texto del documento nunca se persiste).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_persistence.py tests/test_route.py -q` -- expected: verde (roundtrip, `original_text == ""`, 404 en id inexistente).
