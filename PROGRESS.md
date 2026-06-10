# HU Analyzer — Log de Progreso

> Actualizar al final de cada sesión de desarrollo.

---

## Estado del proyecto

**Fase actual:** Sesión 5 completada ✅ — Backend funcional de punta a punta

---

## Módulos

| Módulo | Estado | Notas |
|--------|--------|-------|
| Estructura base del proyecto | ✅ Completo | Sesión 2 |
| Backend: FastAPI setup + CORS | ✅ Completo | Sesión 2 |
| Backend: Pydantic schemas | ✅ Completo | Sesión 2 |
| Backend: Config + variables de entorno | ✅ Completo | Sesión 2 |
| Backend: FileParser (docx, pdf, xlsx, txt) | ✅ Completo | Sesión 3 |
| Backend: BaseModule + módulos de análisis | ✅ Completo | Sesión 4 |
| Backend: Analyzer + integración Claude API | ✅ Completo | Sesión 5 |
| Backend: Endpoint `/api/v1/analyze` (completo) | ✅ Completo | Sesión 5 |
| Backend: Extracción global (objetivo/stakeholders/reglas) | ✅ Completo | Sesión 5 |
| Frontend: Setup React + Vite + Tailwind | ⬜ Pendiente | Sesión 6 |
| Frontend: Componente FileUpload | ⬜ Pendiente | Sesión 6 |
| Frontend: Vista de resultados por HU | ⬜ Pendiente | Sesión 6 |
| Frontend: Vista resumen del proyecto | ⬜ Pendiente | Sesión 6 |
| Integración frontend ↔ backend | ⬜ Pendiente | Sesión 7 |
| Pruebas con archivos reales | ⬜ Pendiente | Sesión 7 |

---

## Decisiones tomadas — Sesión 5

- **Un llamado a Claude por HU:** prompt compuesto con criterios de todos los módulos → respuesta JSON con clave por módulo → cada módulo parsea su sección
- **Segundo llamado global:** al finalizar todas las HU, un llamado adicional extrae objetivo, stakeholders y reglas de negocio del conjunto completo
- **Parser JSON robusto:** `_extract_json` maneja JSON puro, bloques ```json```, y búsqueda con regex — Claude a veces envuelve aunque se le diga que no
- **Errores Anthropic tipados:** `AuthenticationError`, `RateLimitError`, `APIError` → cada uno retorna HTTP correcto (500, 429, 500)
- **Modelo:** `claude-sonnet-4-5` — balance costo/calidad para análisis semántico

---

## Archivos creados/modificados — Sesión 5

```
backend/app/services/analyzer.py          ← NUEVO — Analyzer completo
backend/app/api/v1/routes/analyze.py      ← actualizado — endpoint funcional sin stubs
```

---

## Flujo completo (backend operativo)

```
POST /api/v1/analyze  (archivo)
  → Validar tipo y tamaño
  → FileParser → list[ParsedHU]
  → Por cada HU:
      → Prompt compuesto (criterios de 5 módulos)
      → Claude API → JSON
      → Cada módulo parsea su sección → ModuleResult
      → Score ponderado
  → Llamado global → ProjectSummary
  → AnalyzeResponse
```

---

## Cómo levantar el backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # poner ANTHROPIC_API_KEY real
uvicorn app.main:app --reload
# Swagger → http://localhost:8000/docs
# Probar con POST /api/v1/analyze subiendo un .txt con HU de prueba
```

---

## Deuda técnica

- PDFs escaneados sin texto → agregar OCR (pytesseract) en iteración futura
- Word con HU en tablas → iteración futura
- Las HU se analizan secuencialmente → se puede paralelizar con `asyncio.gather` si el volumen crece
