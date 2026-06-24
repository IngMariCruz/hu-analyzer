---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - '_bmad-output/planning-artifacts/prds/prd-hu-analyzer-2026-06-23/prd.md'
  - '_bmad-output/project-context.md'
  - 'ARCHITECTURE.md'
  - 'CONVENTIONS.md'
  - 'PROGRESS.md'
workflowType: 'architecture'
project_name: 'hu-analyzer'
user_name: 'Mcruz'
date: '2026-06-23'
---

# Architecture Decision Document — HU Analyzer (v1)

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (31, en 8 grupos):**
- **Ingesta (FR1–FR4):** upload de un documento PDF/.docx/.txt/.xlsx, extracción de texto por tipo, validación de tipo/tamaño, **procesamiento en memoria sin persistir**.
- **Validación de pertinencia/validez (FR5–FR9):** el LLM decide si hay proyecto → alerta; si lo hay, decide si la info es válida → si no, mensaje + qué falta; si sí, continúa.
- **Evaluación de HUs (FR10–FR17):** segmentación, checks (formato Como/Quiero/Para, INVEST, coherencia, ambigüedad/contradicción), score 1–100 por HU, bandas, promedio simple.
- **Inferencia de negocio (FR18–FR20):** objetivo, usuarios finales, reglas de negocio.
- **Sugerencias (FR21):** por HU con score < 90.
- **Reportes PDF (FR22–FR24):** reporte de reglas de negocio + reporte de validación de HUs, descargables.
- **Roles/acceso (FR25–FR27):** usuario anónimo gratis; admin autenticado; admin no ve documentos.
- **Métricas (FR28–FR31):** registro de uso, conteos por día/semana/mes/año, métricas por banda, vista de resultados sin documentos.

**Non-Functional Requirements:**
- **Privacidad por diseño:** los documentos HU nunca se persisten; solo resultados y métricas. El panel admin nunca expone documentos ni texto extraído.
- **LLM:** GPT-4o mini (OpenAI); manejo explícito de timeout/error/respuesta mal formada con mensaje claro + reintento; estado de carga.
- **Costo:** un solo envío del documento al LLM por análisis; modelo económico a propósito.
- **Archivos:** tamaño máx. configurable (default 10 MB); tipos PDF/.docx/.txt/.xlsx; rechazo previo al procesamiento.
- **Idioma:** entrada/salida principalmente español.
- **Escala:** demo/portafolio; objetivo < ~60 s para documento típico (≤ ~15 HUs); baja concurrencia.
- **Seguridad:** panel admin autenticado; credenciales no expuestas en el cliente.

**Scale & Complexity:**
- Primary domain: full-stack web (FastAPI + React/Vite/Tailwind) con dependencia de OpenAI.
- Complexity level: media.
- Componentes arquitectónicos estimados (~7): parser de archivos, orquestador LLM/Analyzer, módulos de análisis (Strategy), capa de inferencia de negocio, generador de PDF, persistencia de resultados/métricas, auth + panel admin.

### Technical Constraints & Dependencies

- **Brownfield:** se conserva FastAPI + patrón Strategy de módulos (`BaseModule` + checkers en `services/modules/`) y el frontend React/Vite/Tailwind desacoplado.
- **Migración obligatoria:** Anthropic/Claude → OpenAI GPT-4o mini (en `services/analyzer.py` + prompts `PROMPT_*` de cada módulo); reescritura de la escala 1–10 → 1–100.
- **Dependencia externa:** API de OpenAI (clave en `.env`, costo, disponibilidad y **política de retención de inputs**).
- Generación de PDF server-side (`reportlab`, ya introducido en commits recientes — `report.py`, `downloadReport`).

### Cross-Cutting Concerns Identified

- **Privacidad/no-persistencia** del documento — atraviesa ingesta, modelo de datos, logs y generación de PDF.
- **Resiliencia del LLM** — timeouts, errores, JSON mal formado; afecta toda la cadena de análisis.
- **Costo y abuso** — usuario anónimo sin signup → minimizar tokens y proteger con rate-limiting + tope de tamaño.
- **Autenticación** del panel admin frente al acceso anónimo del usuario.
- **Persistencia de resultados desacoplada de identidad** (anonimato + métricas históricas).

### Hallazgos de la ronda Party Mode (a incorporar en las decisiones)

Surgidos del debate entre Arquitecto, Ingeniera, PM y Analista; se registran aquí para guiar el resto del workflow:

1. **Frontera documento/resultado (Mary).** El **texto extraído crudo es "documento", no "resultado"** (reconstruye 1:1 el original) → no debe persistirse. Las **inferencias en lenguaje natural pueden filtrar verbatim** sensible (nombres, identificadores). → **Nueva NFR de minimización:** el LLM debe *abstraer, no citar*; prohibir nombres propios/identificadores/verbatim en campos persistidos. Si los resultados contienen verbatim, el admin estaría viendo el documento disfrazado de resultado.
2. **Retención del proveedor LLM (Mary).** OpenAI puede retener inputs de API por defecto; el documento "no persistido" de nuestro lado puede vivir en un tercero. → Gestionar opt-out / zero-data-retention y **redactar el NFR de privacidad con honestidad** (el texto se transmite a un tercero para análisis).
3. **Desacople de proveedor LLM (Winston/Amelia).** Introducir una interfaz `LLMProvider` (un puerto con un método) detrás de la cual viva el adaptador OpenAI; facilita futuros cambios y testing con mocks.
4. **Una sola llamada estructurada (Winston/Amelia).** Preferir una llamada por documento con **Structured Outputs / JSON schema** (elimina el JSON malformado en origen) + un reintento con backoff solo en 429/5xx/timeout. Los **checkers Strategy mutan** de "orquestar su propia llamada" a "interpretar y puntuar su sección del JSON".
5. **Escala centralizada (Winston/Amelia).** Normalización de score y definición de bandas en un solo lugar (capa de agregación), no dispersa por checker; auditar `* 10`, `<= 10`, `le=10` en schemas Pydantic y en ambos PDFs.
6. **Modelo de datos sin identidad (Mary/Amelia).** `analysis` (UUID, created_at, story_count, duration_ms, model_version, status) + `story_result` (analysis_id, score, inferencias abstraídas). **Bandas calculadas en query**, no almacenadas. Sin user_id/IP/session/email. `analysis_id` opaco devuelto al cliente para recuperar su resultado en sesión, sin auth.
7. **Rate-limiting efímero (Mary/Winston).** Identificador (IP/token) solo en runtime efímero (memoria/Redis con TTL corto), **nunca persistido** en la base analítica. Tope de tamaño/páginas desde el día uno.
8. **PDF desde el resultado persistido (Winston/Amelia).** Nunca re-leer el documento original para generar el PDF (refuerza la NFR). Builder común para ambos reportes. `reportlab` síncrono bloquea el event loop async — tolerable en demo, identificado como punto de saturación.
9. **Disciplina de scope (John).** El diferenciador es la **inferencia de reglas de negocio**; auth + métricas + dos roles + PDF es andamiaje. Lo único sub-construido es *la evidencia de que la inferencia es buena*. Validar GPT-4o mini vs. el modelo previo específicamente en la sección de reglas con 3 HUs reales, antes de cerrar la decisión del modelo.
10. **Edge cases de métricas (Mary):** documento de 0 historias (¿`story_count=0`?), documento truncado (¿métrica = evaluadas o enviadas?), fallo a mitad (necesita `status` para no contaminar métricas), política de retención de resultados, reidentificación por agregación fina, logs como fuga lateral (NFR: no loguear contenido de documento ni prompt).

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web (FastAPI backend + React/Vite frontend) con orquestación de LLM. **Proyecto brownfield**: la fundación ya está establecida; no se adopta un starter nuevo para no destruir trabajo existente.

### Starter Options Considered

Ninguno nuevo. Se evaluó si reemplazar la base por un meta-framework (Next.js full-stack, T3) y se **descartó**: separaría innecesariamente del backend Python/FastAPI que es donde vive el núcleo (orquestación LLM, parsers, Strategy), y tiraría código brownfield funcional. El frontend desacoplado React/Vite ya cumple.

### Selected Foundation: stack brownfield existente

**Rationale:** la base ya implementa el patrón Strategy, el desacople front/back y los parsers; conservarla es la decisión de mayor valor. El trabajo de v1 es *evolución* (migración LLM, escala 1–100, persistencia de resultados, auth/panel admin, PDF), no *reconstrucción*.

**Architectural Decisions ya provistas por la fundación:**
- **Lenguaje & runtime:** Python 3.11 (backend, async/await), JS/JSX (frontend).
- **Backend framework:** FastAPI, rutas versionadas `/api/v1/...`, Pydantic para schemas.
- **Frontend:** React 18 + Vite (HMR, proxy `/api → backend` en dev), TailwindCSS.
- **Styling:** Tailwind (paleta violeta, fuentes Inter + JetBrains Mono).
- **Patrón de análisis:** Strategy (`BaseModule` + checkers en `services/modules/`).
- **PDF:** reportlab server-side (ya introducido).
- **Config/env:** python-dotenv (`.env` con clave de API, CORS origin, tamaño máx.).
- **Convenciones:** PEP8/snake_case (Python), PascalCase componentes/camelCase (React), errores `{detail, code}`.

**Versiones verificadas (junio 2026):**
- OpenAI Python SDK vigente; **GPT-4o mini soporta Structured Outputs** (`response_format` con `json_schema` + Pydantic) — elimina el JSON malformado en origen. Existen modelos más nuevos/baratos (GPT-5.4 mini, o4-mini) que quedan como opción futura vía la interfaz `LLMProvider`.
- FastAPI 0.138.0 (requiere Python ≥ 3.10; el proyecto usa 3.11 ✅).
- React 18 + Vite + Tailwind: stack vigente; versiones exactas a confirmar al reinstalar.

**Versiones a fijar/actualizar al iniciar implementación:**
- Añadir `openai` (SDK actual) y **retirar** `anthropic` de `requirements.txt`.
- Confirmar FastAPI/Pydantic/React/Vite a sus versiones vigentes en el primer story de setup.

**Nota:** la migración del SDK (Anthropic→OpenAI) y la limpieza de dependencias deberían ser de los primeros stories de implementación.

## Core Architectural Decisions

### Decision Priority Analysis

**Críticas (bloquean implementación):** proveedor LLM + estrategia de orquestación, modelo de datos sin identidad, persistencia (SQLite), privacidad/minimización, auth del admin.
**Importantes (moldean la arquitectura):** centralización de escala/bandas, gate de pertinencia/validez, generación de PDF, rate-limiting.
**Diferidas (post-demo):** Postgres/cloud, Redis para rate-limit, zero-data-retention formal con OpenAI, OCR, paralelización avanzada.

### Data Architecture
- **Motor:** **SQLite** (archivo local). Acceso vía **SQLAlchemy** (ORM). Migraciones: esquema inicial por código; Alembic opcional si el esquema evoluciona.
- **Modelo (sin identidad):**
  - `analysis`: `id` (UUID), `created_at` (UTC), `story_count`, `overall_score`, `duration_ms`, `model_version`, `status` (`ok` | `no_project` | `invalid` | `partial` | `error`), `file_type`.
  - `story_result`: `id`, `analysis_id` (FK), `hu_index`, `score` (1–100), `format_ok`, `invest_notes`, `coherence_notes`, `suggestions` (JSON).
  - `business_inference`: `analysis_id` (FK), `objective`, `end_users` (JSON), `business_rules` (JSON) — **abstraídas, sin verbatim** (NFR de minimización).
- **Bandas:** calculadas en query/aplicación, **no almacenadas**.
- **Sin** tablas de usuario/IP/sesión/email. `analysis_id` opaco devuelto al cliente para recuperar su resultado en la sesión.
- **Métricas admin:** agregaciones `GROUP BY` sobre `analysis.created_at` (día/semana/mes/año) y distribución por banda derivada de `story_result.score` / `analysis.overall_score`.

### Authentication & Security
- **Admin:** login con **password hasheado** (passlib/bcrypt), credenciales en `.env`; respuesta = **JWT** firmado (pyjwt/python-jose) con expiración. Dependencia FastAPI protege rutas `/api/v1/admin/*`.
- **Usuario de internet:** sin auth (anónimo).
- **Rate-limiting:** **en memoria, efímero** (p. ej. slowapi por IP con ventana deslizante); la IP **nunca** se persiste. Tope de tamaño/páginas del documento antes de procesar.
- **Privacidad:** documento en memoria (`BytesIO`), sin `tempfile`; verificar spill-to-disk de `UploadFile`; prohibido loguear contenido/prompt; NFR de minimización en los prompts de inferencia.

### API & Communication Patterns
- REST versionada `/api/v1/...`; errores `{detail, code}` (convención existente).
- Endpoints (estimado): `POST /api/v1/analyze` (anónimo), `GET /api/v1/analyze/{analysis_id}`, `GET /api/v1/report/{analysis_id}?type=business|hu` (PDF), `POST /api/v1/admin/login`, `GET /api/v1/admin/metrics`, `GET /api/v1/admin/analyses`.
- **Orquestación LLM (híbrida):** 1 llamada nivel-documento (pertinencia → validez → inferencia de negocio) + 1 llamada por HU en paralelo (`AsyncOpenAI` + `asyncio.gather` + semáforo). `max_retries` del SDK + timeout por llamada; backoff solo en 429/5xx/timeout. Gate: si "no proyecto" o "info no válida", se corta antes del scoring por-HU.

### Frontend Architecture
- React 18 + Vite + Tailwind; estado local con hooks (sin Redux). Proxy `/api → backend` en dev.
- Flujo: upload → loading → (alerta | mensaje-replantear | resultados). Vista admin separada tras login (panel de métricas + lista de resultados, sin documentos).

### Infrastructure & Deployment
- **Local** (uvicorn + Vite dev / build estático). Sin CI/CD para la demo.
- `.env`: `OPENAI_API_KEY`, `ADMIN_PASSWORD_HASH`, `JWT_SECRET`, `FRONTEND_ORIGIN`, `MAX_FILE_SIZE_MB`, `LLM_MODEL`.
- Logging: solo metadatos (tamaño, tipo, duración, tokens), nunca contenido.

### Decision Impact Analysis

**Secuencia de implementación sugerida:**
1. Migrar SDK Anthropic→OpenAI detrás de `LLMProvider` + retirar `anthropic`.
2. Centralizar escala 1–100/bandas; auditar `*10`/`le=10` en schemas y PDFs.
3. Gate de pertinencia/validez + orquestación híbrida.
4. Persistencia SQLite (modelos sin identidad) + recuperación por `analysis_id`.
5. PDF desde resultado persistido (builder común).
6. Auth admin (JWT) + endpoints de métricas.
7. Rate-limiting efímero + topes de archivo.

**Dependencias cruzadas:** la NFR de minimización condiciona los prompts de inferencia *y* lo que persiste `business_inference`; SQLite + agregaciones condicionan el panel admin; `LLMProvider` habilita test con mocks.
