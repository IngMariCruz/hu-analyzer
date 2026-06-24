---
title: 'Story 1.8 — Inferencia de negocio con minimización'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Inferir objetivo del proyecto, usuarios finales y reglas de negocio, abstrayendo sin citar verbatim ni incluir nombres propios/identificadores (NFR de minimización).

## Resultado
Nuevo `app/services/inference.py` con `infer_business(parsed_hus, provider) -> BusinessInferenceResponse` (llamada nivel-documento, Structured Outputs). Prompt con regla estricta de minimización (prohíbe nombres propios, identificadores y verbatim) y `end_users` SOLO usuarios finales (no equipos técnicos/QA). El esquema `BusinessInferenceResponse(objective, end_users, business_rules)` alimenta `ProjectSummary` (campo `stakeholders` reutilizado para usuarios finales; el frontend rotula "Usuarios finales"). La inferencia se persiste en `business_inference` (1.9).

## Cubre
FR18, FR19, FR20 (+ NFR2 minimización).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_analyzer.py -q` -- expected: verde (FakeProvider devuelve la inferencia; `inference_calls == 1`).
