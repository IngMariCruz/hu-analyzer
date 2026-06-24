---
title: 'Story 1.6 — Calificación 1–100, bandas y promedio'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Centralizar la normalización de score (1–10 → 1–100) y la definición de bandas en un único lugar (capa de agregación), no dispersas por checker. Auditar `*10`/`<=10`/`le=10` en schemas y PDFs.

## Resultado
Nuevo `app/services/scoring.py`: `BANDS` (90 Excepcional / 70 Bueno / 50 Regular / 0 Crítico), `band_for`, `normalize_to_100` (clamp [1,100]), `aggregate_hu_score` (pondera 0–10 → 1–100) y `overall_average` (promedio simple). `HUResult.score` ahora `int` `ge=1 le=100` + `band`; `AnalyzeResponse.overall_score` `le=100` + `overall_band`. `pdf_generator` usa `band_for` y muestra `/100`. Auditoría: el único `*10` restante es la normalización intencional.

## Cubre
FR15, FR16, FR17.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_scoring.py tests/test_analyzer.py -q` -- expected: verde.
