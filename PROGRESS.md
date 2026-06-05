# HU Analyzer — Log de Progreso

> Actualizar al final de cada sesión de desarrollo.

---

## Estado del proyecto

**Fase actual:** Sesión 3 completada ✅

---

## Módulos

| Módulo | Estado | Notas |
|--------|--------|-------|
| Estructura base del proyecto | ✅ Completo | Sesión 2 |
| Backend: FastAPI setup + CORS | ✅ Completo | Sesión 2 |
| Backend: Pydantic schemas | ✅ Completo | Sesión 2 |
| Backend: Config + variables de entorno | ✅ Completo | Sesión 2 |
| Backend: FileParser (docx, pdf, xlsx, txt) | ✅ Completo | Sesión 3 |
| Backend: BaseModule + módulos de análisis | ⬜ Pendiente | Sesión 4 |
| Backend: Integración Claude API | ⬜ Pendiente | Sesión 5 |
| Backend: Endpoint `/api/v1/analyze` (completo) | ⬜ Pendiente | Sesión 5 |
| Backend: Extracción global (objetivo/stakeholders/reglas) | ⬜ Pendiente | Sesión 5 |
| Frontend: Setup React + Vite + Tailwind | ⬜ Pendiente | Sesión 6 |
| Frontend: Componente FileUpload | ⬜ Pendiente | Sesión 6 |
| Frontend: Vista de resultados por HU | ⬜ Pendiente | Sesión 6 |
| Frontend: Vista resumen del proyecto | ⬜ Pendiente | Sesión 6 |
| Integración frontend ↔ backend | ⬜ Pendiente | Sesión 7 |
| Pruebas con archivos reales | ⬜ Pendiente | Sesión 7 |

---

## Decisiones tomadas por sesión

### Sesión 3 — FileParser

- **Segmentación por patrones regex:** detecta `HU-01`, `HU01`, `HU 01`, `US-01`, `1.`, `Historia 1`
- **Fallback:** si no detecta patrones de HU, trata el documento completo como una sola HU
- **Excel (.xlsx):** cada fila = una HU; detecta automáticamente si hay fila de encabezados con columnas relevantes (hu, descripción, etc.)
- **Word (.docx):** respeta los Headings del documento para ayudar a la segmentación
- **PDF:** extrae por página y une con doble salto de línea
- **TXT:** prueba utf-8 → latin-1 → cp1252 para manejar distintas codificaciones
- La ruta `/analyze` ya valida tamaño del archivo (MAX_FILE_SIZE_MB) y llama a `parse_file`
- El endpoint retorna HTTP 501 con conteo de HU encontradas hasta que Sesión 5 esté lista

---

## Archivos creados/modificados en Sesión 3

```
backend/app/services/file_parser.py    ← NUEVO — ParsedHU, ParseResult, parsers por tipo
backend/app/api/v1/routes/analyze.py   ← actualizado — integra FileParser + validación de tamaño
```

---

## Cómo levantar el backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Editar con tu ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Swagger en: http://localhost:8000/docs  
ReDoc en:   http://localhost:8000/redoc

---

## Problemas conocidos / Deuda técnica

- PDFs escaneados (imagen) no tienen texto extraíble con pdfplumber — se puede agregar OCR en el futuro con pytesseract.
- Documentos Word con tablas de HU no están soportados aún — se puede agregar en iteración futura.
