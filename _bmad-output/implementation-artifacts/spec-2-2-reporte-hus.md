---
title: 'Story 2.2 — Reporte de validación de HUs'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Reporte "Validación de HUs": por HU su score, banda, observaciones y sugerencias, más la calificación general. Reusa el builder común.

## Resultado
`build_hu_report(result)` en `pdf_generator.py`: portada ("Validación de Historias de Usuario") + `_build_hu_section` por HU (score 1–100, banda, observaciones, sugerencias) usando `_render`. Expuesto en `GET /api/v1/report/{analysis_id}?type=hu`. Comparte estilos, colores por banda y portada con el reporte de negocio.

## Cubre
FR23, FR24 (descarga).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_report.py -q` -- expected: verde (`type=hu` 200 `application/pdf`).
