---
title: 'Story 1.4 — Segmentación del documento en HUs'
type: 'feature'
created: '2026-06-23'
status: 'done'
---

## Intent
Separar el documento en HUs individuales; si no se detecta ninguna, reportar `story_count: 0` sin fallar.

## Resultado
Preexistente y confirmado: `_segment_hus` segmenta por patrones (HU/US/numeración) con fallback a un bloque único. El route reporta `story_count` desde `total_found` y devuelve respuesta `ok` con `story_count: 0` cuando no hay HUs (sin excepción). Tests de segmentación múltiple y fallback.

## Cubre
FR10.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_parser.py -q` -- expected: verde.
