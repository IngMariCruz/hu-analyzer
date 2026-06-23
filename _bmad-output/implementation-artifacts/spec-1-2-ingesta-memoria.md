---
title: 'Story 1.2 — Subida y extracción de texto en memoria'
type: 'feature'
created: '2026-06-23'
status: 'done'
---

## Intent
Subir PDF/Word/TXT/Excel y extraer su texto en memoria, sin almacenar el documento.

## Resultado
Mayormente preexistente y confirmado: `file_parser.py` parsea con `io.BytesIO` (sin `tempfile` propio); el route valida tipo y tamaño antes de procesar y no loguea contenido. Se añadió `raw_text` a `ParseResult` (para el gate) y tests de extracción TXT.

## Cubre
FR1, FR2, FR3, FR4.

## Deferred
Spill-to-disk de `UploadFile` (SpooledTemporaryFile de Starlette para archivos grandes) → endurecer en Story 1.11.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_parser.py -q` -- expected: verde.
