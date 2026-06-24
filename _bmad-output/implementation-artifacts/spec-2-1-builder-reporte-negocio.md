---
title: 'Story 2.1 — Builder común de PDF y reporte de reglas de negocio'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Builder común reutilizable para ambos reportes PDF (reportlab) + reporte "Validación de reglas de negocio" (objetivo, usuarios finales, reglas), generado SOLO desde el resultado persistido, sin re-leer el documento.

## Resultado
`pdf_generator.py` refactorizado: `_render(story, title)` (builder común A4) + `build_business_report(result)` (portada + objetivo/usuarios finales/reglas). Portada parametrizada (`subtitle`). Nuevo `GET /api/v1/report/{analysis_id}?type=business` carga vía `load_analysis` y arma el PDF; 404 si no existe, 422 si el tipo es inválido. `generate_pdf` (combinado) se conserva para `POST /report` en sesión.

## Cubre
FR22, FR24 (descarga).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_report.py -q` -- expected: verde (builder devuelve `%PDF-`, endpoint 200 `application/pdf` desde resultado persistido, 404, 422).
