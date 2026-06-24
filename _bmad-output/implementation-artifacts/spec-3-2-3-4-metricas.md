---
title: 'Stories 3.2–3.4 — Métricas de uso, bandas y listado'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
- 3.2: usos por día/semana/mes/año (`GROUP BY` sobre `analysis.created_at`).
- 3.3: distribución (conteo y %) por banda, calculada en query desde los scores.
- 3.4: listado de análisis (fecha, score, banda, estado), sin documentos.

## Resultado
Nuevo `app/services/metrics.py`: `usage_by_period` (`func.strftime` por día/semana/mes/año), `band_distribution` (cuenta `overall_score` de status `ok`/`partial` y bucketea con `band_for`; %), `list_analyses` (orden desc, mapea id/created_at/status/story_count/overall_score/banda/file_type). Rutas protegidas: `GET /admin/metrics`, `GET /admin/metrics/bands`, `GET /admin/analyses`. Las bandas no se almacenan; ningún endpoint expone documentos ni texto extraído (no existen en persistencia).

## Cubre
FR29, FR30, FR31 (+ FR27/NFR1: admin nunca ve documentos).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_admin.py -q` -- expected: verde (distribución Excepcional/Crítico correcta; listado con `band`/`status` y sin `original_text`).
