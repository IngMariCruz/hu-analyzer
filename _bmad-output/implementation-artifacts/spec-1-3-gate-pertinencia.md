---
title: 'Story 1.3 — Gate de pertinencia y validez del documento'
type: 'feature'
created: '2026-06-23'
status: 'done'
---

## Intent
Antes de analizar, clasificar el documento vía LLM: `no_project` (alerta, no analiza), `invalid` (replantear + qué falta), `ok` (continúa).

## Resultado
Nuevo `app/services/gate.py` con `check_document(raw_text, provider=None) -> GateResult` (llamada LLM nivel-documento, Structured Outputs). `GateResult` (status Literal + message) en `llm/schemas.py`. El route ejecuta el gate tras parsear y corta con `_gate_response(...)` si no es `ok`. `AnalyzeResponse` ahora lleva `status`, `message`, `story_count`.

## Cubre
FR5, FR6, FR7, FR8, FR9.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_gate.py -q` -- expected: verde.
