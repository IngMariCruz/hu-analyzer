# HU Analyzer — Log de Progreso

> Actualizar al final de cada sesión de desarrollo.

---

## Estado del proyecto

**Fase actual:** Sesión 4 completada ✅

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
| Backend: Integración Claude API + Analyzer | ⬜ Pendiente | Sesión 5 |
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

### Sesión 4 — Módulos de análisis

- **Patrón Strategy confirmado:** cada módulo hereda `BaseModule` e implementa `parse_response`
- **Un solo prompt compuesto:** el `Analyzer` (Sesión 5) enviará UN llamado a Claude con los criterios de todos los módulos embebidos → respuesta JSON con clave por módulo → cada módulo parsea su sección
- **Pesos finales:** FormatChecker 20% · UserChecker 20% · FunctionalityChecker 20% · InvestChecker 25% · CoherenceChecker 15% → suma exacta 1.0
- **Registro central:** `services/modules/__init__.py` → `ACTIVE_MODULES` — agregar un módulo nuevo solo requiere crear el archivo y registrarlo aquí

### Sesión 3 — FileParser
- Segmentación por regex; fallback a documento completo si no hay patrones
- Excel: cada fila = HU; detección automática de encabezados
- TXT: prueba utf-8 → latin-1 → cp1252

### Sesión 2 — Base del backend
- pydantic-settings para variables de entorno
- Schemas: HUResult, ProjectSummary, AnalyzeResponse, ErrorResponse
- Endpoint /analyze con validación de tipo y tamaño de archivo

### Sesión 1 — Planeación
- Stack: FastAPI + React + Vite + TailwindCSS
- Tipos de archivo: .docx, .pdf, .xlsx, .txt

---

## Archivos creados en Sesión 4

```
backend/app/services/modules/
├── base_module.py              ← BaseModule abstracta + ModuleResult dataclass
├── format_checker.py           ← Valida estructura Como/Quiero/Para (peso 20%)
├── user_checker.py             ← Valida usuario de negocio, no técnico (peso 20%)
├── functionality_checker.py    ← Valida funcionalidad única + objetivo claro (peso 20%)
├── invest_checker.py           ← Evalúa criterios de aceptación vs INVEST (peso 25%)
├── coherence_checker.py        ← Detecta ambigüedad y contradicciones (peso 15%)
└── __init__.py                 ← ACTIVE_MODULES — registro central de módulos
```

---

## Cómo levantar el backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # agregar ANTHROPIC_API_KEY
uvicorn app.main:app --reload
# Swagger → http://localhost:8000/docs
```

---

## Deuda técnica

- PDFs escaneados (imagen) no tienen texto extraíble → agregar OCR con pytesseract en iteración futura
- Word con HU en tablas no soportado aún → iteración futura
- Múltiples llamadas a Claude se pueden optimizar con batch en el futuro
