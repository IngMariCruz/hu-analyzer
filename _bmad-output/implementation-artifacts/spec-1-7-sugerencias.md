---
title: 'Story 1.7 — Sugerencias de mejora por HU'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Generar sugerencias concretas para las HU con calificación < 90; las HU con score ≥ 90 no las requieren.

## Resultado
En `analyzer._build_hu_result`, tras calcular el score 1–100, si `score >= SUGGESTION_THRESHOLD (90)` se vacían las `suggestions`. El prompt por-HU instruye dejar `suggestions` vacío cuando el criterio es excelente, de modo que la generación se concentra en lo mejorable. Test dedicado verifica que una HU con score ≥ 90 no lleva sugerencias.

## Cubre
FR21.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_analyzer.py::test_analyze_suggestions_only_below_90 -q` -- expected: verde.
