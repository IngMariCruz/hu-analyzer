# HU Analyzer — Documento de Arquitectura

> **Versión:** 1.1 (implementada — Epics 1–3)
> **Estado:** v1 funcionalmente completa
> **Propósito:** Fuente de verdad para todas las sesiones de desarrollo. Pegar al inicio de cada sesión.
> **Nota:** la arquitectura detallada de v1 vive en [`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md); este archivo resume el estado implementado.

---

## 1. Descripción del sistema

Sistema web que recibe un archivo con Historias de Usuario (HU) redactadas, las analiza con IA y devuelve:
- **Gate** previo: avisa si el documento no es un proyecto (`no_project`) o si la info no es válida (`invalid`).
- Calificación por HU **(1–100)** con banda (Excepcional/Bueno/Regular/Crítico) y promedio del documento.
- Retroalimentación + sugerencias (para HU con score < 90).
- Inferencia de negocio **abstraída** (sin verbatim/PII): objetivo, usuarios finales, reglas de negocio.
- Reportes PDF descargables (reglas de negocio · validación de HUs) desde el resultado persistido.
- Panel admin (JWT) con métricas de uso, distribución por banda y listado de análisis — **sin documentos**.
- Privacidad por diseño: el documento y el texto extraído **nunca** se persisten.

---

## 2. Stack tecnológico

| Capa       | Tecnología          | Justificación                              |
|------------|---------------------|--------------------------------------------|
| Backend    | Python 3.11 + FastAPI | Async nativo, fácil extensión de rutas   |
| IA         | **OpenAI GPT-4o mini** (vía interfaz `LLMProvider`) | Structured Outputs; proveedor intercambiable |
| Persistencia | **SQLite + SQLAlchemy 2.0** | Resultados/métricas sin identidad        |
| Reportes   | reportlab           | PDF server-side desde el resultado persistido |
| Auth admin | **PyJWT + bcrypt**  | JWT firmado + password hasheado            |
| Rate-limit | **slowapi**         | Límite por IP en memoria efímera           |
| Frontend   | React 18 + Vite     | Componentes reutilizables, build rápido    |
| Estilos    | TailwindCSS         | Utilidades, sin overhead de diseño         |
| Parsers    | python-docx, pdfplumber, openpyxl | Un parser por tipo de archivo |
| Env/Config | pydantic-settings (.env) | Variables de entorno seguras          |

---

## 3. Estructura de carpetas

```
hu-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI, CORS, lifespan(init_db), rate-limiter
│   │   ├── api/v1/routes/
│   │   │   ├── analyze.py           # POST /analyze · GET /analyze/{id}
│   │   │   ├── report.py            # GET /report/{id}?type=business|hu · POST /report
│   │   │   └── admin.py             # POST /admin/login · GET /admin/metrics[/bands] · /admin/analyses
│   │   ├── services/
│   │   │   ├── file_parser.py       # Extrae texto + segmenta HU (en memoria)
│   │   │   ├── gate.py              # Gate de pertinencia/validez (LLM nivel-documento)
│   │   │   ├── analyzer.py          # Orquestación híbrida (1 llamada por HU + inferencia)
│   │   │   ├── inference.py         # Inferencia de negocio minimizada
│   │   │   ├── scoring.py           # Escala 1–100 + bandas (centralizado)
│   │   │   ├── persistence.py       # save/load AnalyzeResponse ↔ ORM
│   │   │   ├── metrics.py           # Consultas del panel admin
│   │   │   ├── pdf_generator.py     # Builder común + 2 reportes
│   │   │   ├── llm/                 # LLMProvider (base) + OpenAIProvider + schemas
│   │   │   └── modules/             # Strategy: format/user/functionality/invest/coherence
│   │   ├── db/
│   │   │   ├── models.py            # ORM sin identidad: analysis, story_result, business_inference
│   │   │   └── session.py           # engine + SessionLocal + init_db + get_db
│   │   ├── models/schemas.py        # Pydantic request/response
│   │   └── core/
│   │       ├── config.py            # Settings (.env)
│   │       ├── ratelimit.py         # slowapi Limiter por IP
│   │       └── security.py          # bcrypt + JWT + require_admin
│   ├── tests/                       # pytest (30 tests)
│   ├── requirements.txt
│   └── .env                         # No subir a git
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ResultCard.jsx       # Tarjeta por HU
│   │   │   ├── ScoreBadge.jsx
│   │   │   ├── FeedbackList.jsx
│   │   │   └── ProjectSummary.jsx   # Objetivo, stakeholders, reglas
│   │   ├── services/
│   │   │   └── api.js               # Llamadas al backend
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── ARCHITECTURE.md  ← este archivo
├── CONVENTIONS.md
├── PROGRESS.md
└── README.md
```

---

## 4. Módulos de análisis (patrón Strategy — escalabilidad)

Cada módulo hereda de `BaseModule` y aporta su `analysis_criteria` (para el prompt) y `parse_response` (puntúa su sección del JSON estructurado; ya no orquesta su propia llamada). El score 1–100 y las bandas se calculan en `services/scoring.py`, no en el checker.
Para agregar una nueva funcionalidad basta con crear un archivo en `services/modules/` y registrarlo en `services/modules/__init__.py` (`ACTIVE_MODULES`).

```
BaseModule
├── FormatChecker        → valida estructura "Como / Quiero / Para"
├── UserChecker          → valida que el usuario no sea QA/dev/sistema
├── FunctionalityChecker → valida que sea una sola funcionalidad
├── InvestChecker        → evalúa criterios de aceptación vs INVEST
└── CoherenceChecker     → detecta ambigüedad y contradicciones
```

---

## 5. Modelos de datos (Pydantic)

```python
# Request
class AnalyzeRequest:
    file: UploadFile

# Por cada HU
class HUResult:
    hu_id: str
    original_text: str    # vacío al recuperar por analysis_id (no se persiste)
    score: int            # 1 – 100
    band: str             # Excepcional / Bueno / Regular / Crítico
    evaluated: bool       # False si la HU falló (status del documento: partial)
    feedback: list[str]
    suggestions: list[str]

# Resumen del proyecto (inferencia minimizada)
class ProjectSummary:
    objective: str
    stakeholders: list[str]   # usuarios finales
    business_rules: list[str]

# Respuesta completa
class AnalyzeResponse:
    analysis_id: str | None   # id opaco para recuperar en sesión
    status: str               # ok / partial / no_project / invalid
    message: str | None
    story_count: int
    hu_results: list[HUResult]
    project_summary: ProjectSummary
    overall_score: float      # 0 – 100 (promedio simple)
    overall_band: str
```

### Persistencia (SQLite, sin identidad)

```
analysis(id, created_at, status, story_count, overall_score, duration_ms, model_version, file_type)
story_result(id, analysis_id, hu_index, hu_id, score, evaluated, feedback[JSON], suggestions[JSON])
business_inference(analysis_id, objective, end_users[JSON], business_rules[JSON])
```
> Sin `original_text`, sin user_id/IP/sesión/email. Las bandas se calculan en query, no se almacenan.

---

## 6. Flujo de datos

```
Archivo subido (docx/pdf/xlsx/txt)  → topes de tipo/tamaño + rate-limit
        ↓
   FileParser → texto plano (en memoria, sin tempfile)
        ↓
   Segmentación de HU (por títulos o numeración)
        ↓
   Gate (LLM nivel-documento) → no_project | invalid | ok
        ↓ (ok)
   Orquestación híbrida:
     ├─ 1 llamada por HU en paralelo (asyncio.gather + semáforo) → módulos Strategy
     └─ 1 llamada de inferencia de negocio (minimizada)
        ↓
   Agregación + scoring 1–100 + bandas (services/scoring.py)
        ↓
   Persistir (SQLite, sin documento) → analysis_id opaco
        ↓
   AnalyzeResponse → Frontend     ── PDF: GET /report/{id} desde lo persistido
```

---

## 7. Decisiones de diseño tomadas

| Decisión | Justificación |
|----------|--------------|
| Interfaz `LLMProvider` + Structured Outputs | Proveedor intercambiable, testeable con mocks, JSON válido por construcción |
| Orquestación híbrida (1 llamada por HU + 1 de inferencia) | Paraleliza y aísla fallos por HU (`status: partial`) |
| Escala/bandas centralizadas (`scoring.py`) | Una sola fuente de verdad para 1–100 y bandas |
| Modelo de datos sin identidad; documento nunca persistido | Privacidad por diseño + minimización en inferencias |
| PDF desde el resultado persistido (builder común) | No re-lee el documento; refuerza la privacidad |
| Rate-limiting efímero por IP (slowapi) | Protege costo/abuso sin persistir identidad |
| Módulos Strategy en `services/modules/` | Agregar checks sin tocar el núcleo |
| Frontend desacoplado del backend | Se puede reemplazar cualquiera de los dos |

---

## 8. Variables de entorno requeridas

```env
# backend/.env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
FRONTEND_ORIGIN=http://localhost:5173
MAX_FILE_SIZE_MB=10
LLM_MAX_CONCURRENCY=5
RATE_LIMIT=10/minute
DATABASE_URL=sqlite:///./hu_analyzer.db
# Panel admin (Epic 3)
ADMIN_PASSWORD_HASH=        # python -c "from app.core.security import hash_password; print(hash_password('...'))"
JWT_SECRET=cambia-esto-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```
