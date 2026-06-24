---
title: 'Story 2.3 — Descarga de reportes desde el frontend'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Botones para descargar cada reporte en PDF vía `GET /api/v1/report/{analysis_id}?type=business|hu`; si el resultado ya no está disponible, mensaje claro.

## Resultado
`api.js`: `downloadReportById(analysisId, type)` hace GET, descarga el blob y traduce el 404 a "El análisis ya no está disponible. Vuelve a subir el documento." `App.jsx`: dos botones (`Reglas de negocio` / `Validación de HUs`) vía componente `DownloadButton`, con estado de carga por botón (`downloading`). Si falta `analysis_id`, muestra el mensaje sin llamar al backend.

## Cubre
FR24.

## Verification
- Manual (frontend sin node_modules en repo): `cd frontend && npm install && npm run dev`. Backend cubierto por `tests/test_report.py`.
