# HU Analyzer — Documento de Arquitectura

> **Versión:** 1.0  
> **Estado:** Base aprobada  
> **Propósito:** Fuente de verdad para todas las sesiones de desarrollo. Pegar al inicio de cada sesión.

---

## 1. Descripción del sistema

Sistema web que recibe un archivo con Historias de Usuario (HU) redactadas, las analiza con IA y devuelve:
- Calificación por HU (1–10)
- Retroalimentación detallada con fragmentos corregibles
- Extracción transversal: objetivo del proyecto, stakeholders, reglas de negocio

---

## 2. Stack tecnológico

| Capa       | Tecnología          | Justificación                              |
|------------|---------------------|--------------------------------------------|
| Backend    | Python 3.11 + FastAPI | Async nativo, fácil extensión de rutas   |
| IA         | Anthropic API (Claude) | Análisis semántico de texto              |
| Frontend   | React 18 + Vite     | Componentes reutilizables, build rápido    |
| Estilos    | TailwindCSS         | Utilidades, sin overhead de diseño         |
| Parsers    | python-docx, pdfplumber, openpyxl | Un parser por tipo de archivo |
| Env/Config | python-dotenv       | Variables de entorno seguras               |

---

## 3. Estructura de carpetas

```
hu-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Punto de entrada FastAPI, CORS
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── routes/
│   │   │           └── analyze.py   # Endpoint POST /api/v1/analyze
│   │   ├── services/
│   │   │   ├── file_parser.py       # Extrae texto según tipo de archivo
│   │   │   ├── analyzer.py          # Llama a Claude API, orquesta análisis
│   │   │   └── modules/             # ← CLAVE para escalabilidad
│   │   │       ├── base_module.py   # Clase abstracta BaseModule
│   │   │       ├── format_checker.py
│   │   │       ├── invest_checker.py
│   │   │       └── coherence_checker.py
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic: request/response models
│   │   └── core/
│   │       └── config.py            # Settings (API keys, CORS origins)
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

Cada módulo hereda de `BaseModule` e implementa un método `analyze(hu_text) -> ModuleResult`.
Para agregar una nueva funcionalidad basta con crear un archivo en `services/modules/` y registrarlo en `analyzer.py`.

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
    original_text: str
    score: float          # 1.0 – 10.0
    feedback: list[str]   # Observaciones con citas del texto original
    suggestions: list[str]

# Resumen del proyecto
class ProjectSummary:
    objective: str
    stakeholders: list[str]
    business_rules: list[str]

# Respuesta completa
class AnalyzeResponse:
    hu_results: list[HUResult]
    project_summary: ProjectSummary
    overall_score: float
```

---

## 6. Flujo de datos

```
Archivo subido (docx/pdf/xlsx/txt)
        ↓
   FileParser → texto plano
        ↓
   Segmentación de HU (por títulos o numeración)
        ↓
   Para cada HU → Módulos de análisis → Claude API
        ↓
   Agregación de resultados
        ↓
   Extracción global (objetivo, stakeholders, reglas)
        ↓
   AnalyzeResponse → Frontend
```

---

## 7. Decisiones de diseño tomadas

| Decisión | Justificación |
|----------|--------------|
| Un endpoint por ahora (`/analyze`) | YAGNI; se expande a v2 cuando sea necesario |
| Módulos separados en `services/modules/` | Permite agregar checks sin tocar el núcleo |
| Claude hace el análisis semántico | Evita reglas hardcoded frágiles |
| Frontend desacoplado del backend | Se puede reemplazar cualquiera de los dos |
| Vite en lugar de CRA | Más rápido, menos configuración |

---

## 8. Variables de entorno requeridas

```env
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
FRONTEND_ORIGIN=http://localhost:5173
MAX_FILE_SIZE_MB=10
```
