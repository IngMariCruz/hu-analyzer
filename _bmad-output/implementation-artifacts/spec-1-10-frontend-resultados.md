---
title: 'Story 1.10 — Visualización de resultados en el frontend'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Mostrar estado de carga, alerta (`no_project`) / mensaje de replantear (`invalid`), o resultados (`ok`/`partial`) con promedio + banda, inferencia de negocio y lista de HU (score, banda, observaciones, sugerencias). Ante error del backend, mensaje claro con reintentar.

## Resultado
`App.jsx`: ramifica por `result.status` — `GateAlert` para `no_project`/`invalid`, `PartialBanner` para `partial`, grid de resultados para `ok`/`partial`. `ErrorBanner` ahora con botón **Reintentar** (reusa `lastFile`). `ScoreBadge.jsx` reescrito a escala 1–100 con `bandFor` (Excepcional/Bueno/Regular/Crítico) y export de la función. `ResultCard` muestra banda, estado "No evaluada" (`evaluated=false`) y placeholder cuando `original_text` viene vacío (recuperación). `ProjectSummary` rotula "Usuarios finales" y propaga `overallBand`. `api.js` añade `getAnalysis(analysisId)`.

## Cubre
FR23 (presentación) + NFR3/NFR6 (estado de carga, error sin pantalla en blanco, español).

## Verification
- Manual: `cd frontend && npm install && npm run dev` (no hay node_modules en el repo). Revisión de código de los componentes; el backend cubre la forma de datos con pytest.
