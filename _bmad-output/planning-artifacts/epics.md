---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - '_bmad-output/planning-artifacts/prds/prd-hu-analyzer-2026-06-23/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/project-context.md'
---

# hu-analyzer - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for hu-analyzer, decomposing the requirements from the PRD and Architecture into implementable stories. No UX Design document exists; UX flow is taken from the PRD user journey.

## Requirements Inventory

### Functional Requirements

FR1: El usuario puede subir un archivo en formato PDF, Word (.docx), TXT o Excel (.xlsx).
FR2: El sistema extrae el texto del documento según su tipo de archivo.
FR3: El sistema valida tipo y tamaño de archivo (límite configurable) y rechaza lo no soportado con un mensaje claro.
FR4: El documento se procesa en memoria y no se almacena tras el análisis.
FR5: Mediante el LLM, el sistema determina si el documento contiene información de un proyecto.
FR6: Si no contiene información de un proyecto, muestra una alerta al usuario y no realiza el análisis.
FR7: Si contiene un proyecto, el sistema determina si la información es válida (se comprende el core del negocio).
FR8: Si la información no es válida, indica al usuario que debe replantear el contenido del documento y muestra qué no se comprendió.
FR9: Si la información es válida, el sistema procede con la evaluación y la inferencia de negocio.
FR10: El sistema segmenta el documento en HUs individuales.
FR11: Por cada HU, evalúa el formato "Como / Quiero / Para".
FR12: Por cada HU, evalúa los criterios de aceptación contra INVEST.
FR13: Por cada HU, evalúa la coherencia interna del enunciado.
FR14: El sistema detecta ambigüedades o contradicciones dentro del mismo documento.
FR15: El sistema asigna a cada HU una calificación de 1 a 100.
FR16: El sistema clasifica cada calificación en una banda: 90–100 Excepcional, 70–89 Bueno, 50–69 Regular, < 50 Crítico.
FR17: El sistema calcula y presenta una calificación promedio del documento (promedio simple de las HUs), con su banda.
FR18: El sistema infiere el objetivo del proyecto.
FR19: El sistema infiere los usuarios finales del proyecto (stakeholders, solo usuarios finales).
FR20: El sistema infiere las reglas de negocio.
FR21: Para cada HU con calificación < 90, el sistema genera sugerencias concretas de cómo mejorar su calificación.
FR22: El sistema genera un reporte "Validación de reglas de negocio" (objetivo, usuarios finales, reglas de negocio).
FR23: El sistema genera un reporte "Validación de HUs" (calificación por HU, observaciones, sugerencias, calificación general).
FR24: El usuario puede descargar ambos reportes en PDF.
FR25: El usuario de internet usa la herramienta de forma anónima y gratuita: sube HU y descarga reportes sin registrarse.
FR26: El administrador accede a su panel mediante autenticación.
FR27: El administrador no puede ver los documentos HU subidos por los usuarios.
FR28: El sistema registra cada uso de la herramienta (sin almacenar el documento).
FR29: El panel muestra el número de usos por día, semana, mes y año.
FR30: El panel muestra métricas por banda de calificación.
FR31: El panel muestra los resultados de los análisis, sin los documentos asociados.

### NonFunctional Requirements

NFR1: Privacidad por diseño — los documentos HU nunca se persisten; solo resultados y métricas. El panel admin nunca expone documentos ni texto extraído.
NFR2: Minimización en la inferencia — el LLM debe abstraer, no citar; prohibido nombres propios, identificadores y verbatim en los campos persistidos.
NFR3: LLM GPT-4o mini (OpenAI) — ante timeout/error/respuesta mal formada, mensaje de error claro + reintento; estado de carga visible. Sin pantalla en blanco ni resultado parcial silencioso.
NFR4: Costo — un solo envío del documento al LLM por análisis; sin reenvíos innecesarios.
NFR5: Restricciones de archivo — tamaño máx. configurable (default 10 MB); tipos PDF/.docx/.txt/.xlsx; rechazo antes de procesar.
NFR6: Idioma — entrada/salida principalmente en español.
NFR7: Rendimiento/escala — demo/portafolio, baja concurrencia; objetivo < ~60 s para documento típico (≤ ~15 HUs).
NFR8: Seguridad — panel admin autenticado (JWT); credenciales no expuestas en el cliente; no loguear contenido del documento ni prompt.

### Additional Requirements

(From Architecture — brownfield: FastAPI + React/Vite/Tailwind existentes; conservar patrón Strategy.)

- Introducir interfaz `LLMProvider` y migrar de Anthropic/Claude a OpenAI GPT-4o mini; retirar `anthropic` de dependencias, añadir `openai`.
- Usar Structured Outputs (JSON schema + Pydantic) en las llamadas al LLM.
- Centralizar normalización de score y definición de bandas (escala 1–10 → 1–100); auditar `*10`/`<=10`/`le=10` en schemas Pydantic y en los PDFs.
- Orquestación híbrida: 1 llamada nivel-documento (pertinencia → validez → inferencia de negocio) + 1 llamada por HU en paralelo (`AsyncOpenAI` + `asyncio.gather` + semáforo); gate corta antes del scoring si "no proyecto" o "info no válida".
- Persistencia SQLite vía SQLAlchemy; modelos `analysis`, `story_result`, `business_inference` sin identidad; `analysis_id` opaco para recuperar en sesión; bandas calculadas en query.
- Generación de PDF (reportlab) desde el resultado persistido, nunca re-leyendo el documento; builder común para ambos reportes.
- Auth admin con password hasheado (passlib/bcrypt) en `.env` + JWT firmado; dependencia FastAPI protege `/api/v1/admin/*`.
- Rate-limiting en memoria efímero (slowapi por IP), IP nunca persistida; tope de tamaño/páginas antes de procesar.
- Documento solo en memoria (`BytesIO`), sin `tempfile`; verificar spill-to-disk de `UploadFile`; logging solo de metadatos.
- Variables `.env`: `OPENAI_API_KEY`, `ADMIN_PASSWORD_HASH`, `JWT_SECRET`, `FRONTEND_ORIGIN`, `MAX_FILE_SIZE_MB`, `LLM_MODEL`.

### UX Design Requirements

(No existe documento UX. Flujo tomado del user journey del PRD: upload → loading → alerta | mensaje-replantear | resultados; vista admin separada tras login.)

### FR Coverage Map

| FR | Epic |
|----|------|
| FR1–FR4 (ingesta, procesamiento en memoria) | Epic 1 |
| FR5–FR9 (pertinencia/validez) | Epic 1 |
| FR10–FR17 (evaluación + score/bandas) | Epic 1 |
| FR18–FR20 (inferencia de negocio) | Epic 1 |
| FR21 (sugerencias) | Epic 1 |
| FR25 (uso anónimo) | Epic 1 |
| FR28 (registro de uso) | Epic 1 (consumido en Epic 3) |
| FR22–FR24 (reportes PDF) | Epic 2 |
| FR26 (login admin) | Epic 3 |
| FR27 (admin no ve documentos) | Epic 3 (garantizado por FR4) |
| FR29–FR31 (métricas y resultados) | Epic 3 |

Cobertura: 31/31 FRs.

## Epic List

### Epic 1: Motor de análisis de HUs
El usuario anónimo sube un documento de HUs y recibe en pantalla la evaluación completa (score 1–100 + banda por HU, promedio del documento, observaciones y sugerencias) más la inferencia de objetivo / usuarios finales / reglas de negocio. El resultado queda recuperable por `analysis_id` durante su sesión, sin que el documento se almacene. Incluye la migración a GPT-4o mini tras `LLMProvider`, la escala 1–100 centralizada, el gate de pertinencia/validez y la orquestación híbrida.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR25, FR28

### Epic 2: Reportes descargables en PDF
El usuario descarga dos reportes en PDF —"Validación de reglas de negocio" y "Validación de HUs"— generados desde el resultado persistido (nunca re-leyendo el documento), con un builder común.
**FRs covered:** FR22, FR23, FR24

### Epic 3: Panel de administrador y métricas
El administrador inicia sesión (JWT) y consulta el uso de la herramienta (día/semana/mes/año), las métricas por banda de calificación y los resultados de los análisis, sin acceso a los documentos.
**FRs covered:** FR26, FR27, FR29, FR30, FR31

## Epic 1: Motor de análisis de HUs

El usuario anónimo sube un documento de HUs y recibe la evaluación completa por HU más la inferencia de negocio, sin que el documento se almacene. Stories ordenadas: migración LLM → ingesta → gate → evaluación → score → sugerencias → inferencia → persistencia → frontend → endurecimiento.

### Story 1.1: Abstracción LLMProvider y migración a GPT-4o mini

As a mantenedor del sistema,
I want una interfaz `LLMProvider` con un adaptador OpenAI GPT-4o mini que reemplace la integración Claude,
So that el análisis use el modelo elegido y el proveedor sea intercambiable y testeable.

**Acceptance Criteria:**

**Given** el backend con la integración Anthropic actual en `services/analyzer.py`
**When** se introduce `LLMProvider.complete(...)` con un adaptador OpenAI usando `AsyncOpenAI`
**Then** las llamadas de análisis pasan por la interfaz y usan el modelo definido en `LLM_MODEL` (default `gpt-4o-mini`)
**And** se retira `anthropic` de `requirements.txt` y se añade `openai`
**And** las respuestas usan Structured Outputs (`response_format` con `json_schema` + Pydantic)
**And** existe un test que mockea el proveedor y verifica el parseo del JSON estructurado

### Story 1.2: Subida y extracción de texto en memoria

As a usuario anónimo,
I want subir un archivo PDF, Word, TXT o Excel y que el sistema extraiga su texto sin guardarlo,
So that pueda analizar mis HUs sin que el documento quede almacenado.

**Acceptance Criteria:**

**Given** el endpoint `POST /api/v1/analyze`
**When** subo un archivo de tipo soportado (.pdf/.docx/.txt/.xlsx) dentro del límite de tamaño
**Then** el sistema extrae el texto procesándolo en memoria (`BytesIO`), sin escribir a disco ni usar `tempfile`
**And** si el tipo no es soportado o supera `MAX_FILE_SIZE_MB`, responde con error `{detail, code}` claro antes de procesar
**And** ni el contenido del documento ni el texto extraído se escriben en logs

### Story 1.3: Gate de pertinencia y validez del documento

As a usuario anónimo,
I want que el sistema me avise si el documento no contiene un proyecto o si la información no es válida,
So that sepa que debo subir o replantear el contenido antes de esperar un análisis.

**Acceptance Criteria:**

**Given** un documento con texto extraído
**When** se ejecuta la llamada LLM nivel-documento de pertinencia
**Then** si no contiene información de un proyecto, responde con una alerta y NO continúa el análisis (`status: no_project`)
**And** si contiene un proyecto pero la información no es válida, responde indicando replantear el documento y QUÉ no se comprendió (`status: invalid`)
**And** si la información es válida, continúa hacia la evaluación e inferencia (`status: ok`)

### Story 1.4: Segmentación del documento en HUs

As a usuario anónimo,
I want que el sistema separe el documento en HUs individuales,
So that cada historia se evalúe por separado.

**Acceptance Criteria:**

**Given** un documento válido (`status: ok`)
**When** se procesa el texto
**Then** el sistema identifica y separa las HUs individuales
**And** si no se detecta ninguna HU, registra `story_count: 0` y lo refleja en la respuesta sin fallar

### Story 1.5: Evaluación por HU (formato, INVEST, coherencia, ambigüedad)

As a usuario anónimo,
I want que cada HU se evalúe en formato Como/Quiero/Para, INVEST, coherencia y ausencia de ambigüedad/contradicciones,
So that obtenga retroalimentación de calidad por historia.

**Acceptance Criteria:**

**Given** las HUs segmentadas
**When** se ejecuta la orquestación híbrida (1 llamada por HU en paralelo con `asyncio.gather` + semáforo)
**Then** cada HU recibe evaluación de formato Como/Quiero/Para, criterios INVEST y coherencia interna
**And** se detectan ambigüedades o contradicciones a nivel documento
**And** los checkers Strategy interpretan y puntúan su sección del JSON estructurado (sin orquestar su propia llamada)
**And** ante timeout/error de una HU, se reintenta (backoff en 429/5xx/timeout) y, si persiste, se marca esa HU sin abortar el resto (`status: partial`)

### Story 1.6: Calificación 1–100, bandas y promedio

As a usuario anónimo,
I want una calificación de 1 a 100 por HU con su banda y un promedio del documento,
So that entienda de un vistazo la calidad de mis HUs.

**Acceptance Criteria:**

**Given** las HUs evaluadas
**When** se calcula la puntuación
**Then** cada HU recibe un score en [1,100]
**And** cada score se clasifica en banda (90–100 Excepcional, 70–89 Bueno, 50–69 Regular, <50 Crítico)
**And** se calcula el promedio simple del documento con su banda
**And** la normalización de score y la definición de bandas viven en un único lugar (capa de agregación), no dispersas por checker

### Story 1.7: Sugerencias de mejora por HU

As a usuario anónimo,
I want sugerencias concretas para las HUs con calificación menor a 90,
So that sepa cómo mejorarlas.

**Acceptance Criteria:**

**Given** las HUs calificadas
**When** una HU tiene score < 90
**Then** el sistema genera sugerencias concretas de mejora para esa HU
**And** las HUs con score ≥ 90 no requieren sugerencias

### Story 1.8: Inferencia de negocio con minimización

As a usuario anónimo (analista),
I want que el sistema infiera el objetivo del proyecto, los usuarios finales y las reglas de negocio,
So that pueda validar con el cliente que su idea fue comprendida.

**Acceptance Criteria:**

**Given** un documento válido
**When** se ejecuta la inferencia de negocio
**Then** el resultado incluye objetivo del proyecto, usuarios finales y reglas de negocio
**And** las inferencias abstraen el contenido sin citar verbatim ni incluir nombres propios/identificadores (NFR de minimización)

### Story 1.9: Persistencia del resultado y recuperación por analysis_id

As a usuario anónimo,
I want recuperar el resultado de mi análisis durante mi sesión,
So that pueda volver a verlo sin re-subir el documento, sin que este se almacene.

**Acceptance Criteria:**

**Given** un análisis completado
**When** finaliza el procesamiento
**Then** se persisten `analysis`, `story_result` y `business_inference` en SQLite (vía SQLAlchemy), SIN el documento ni el texto extraído ni PII
**And** se devuelve un `analysis_id` opaco al cliente
**And** `GET /api/v1/analyze/{analysis_id}` recupera el resultado persistido
**And** el registro sirve como evento de uso (FR28) con `created_at`, `story_count`, `overall_score`, `status`, `model_version`

### Story 1.10: Visualización de resultados en el frontend

As a usuario anónimo,
I want ver en pantalla la alerta, el mensaje de replantear o los resultados según el caso,
So that interprete fácilmente el análisis.

**Acceptance Criteria:**

**Given** la app React
**When** subo un documento
**Then** veo un estado de carga durante el análisis
**And** si `status` es `no_project` o `invalid`, veo la alerta o el mensaje de replantear con el detalle
**And** si `status` es `ok`/`partial`, veo el promedio + banda del documento, la inferencia de negocio y la lista de HUs con score, banda, observaciones y sugerencias
**And** ante error del backend veo un mensaje claro con opción de reintentar (sin pantalla en blanco)

### Story 1.11: Endurecimiento — rate-limiting efímero y topes de archivo

As a operador del servicio,
I want limitar el abuso anónimo sin almacenar identidad,
So that el costo del LLM y el servicio estén protegidos.

**Acceptance Criteria:**

**Given** el endpoint anónimo `/api/v1/analyze`
**When** una IP supera el límite de peticiones en la ventana configurada
**Then** el sistema responde con error de rate-limit
**And** el identificador (IP) vive solo en memoria efímera y NUNCA se persiste en la base
**And** se aplican los topes de tamaño/tipo de archivo antes de invocar el LLM

## Epic 2: Reportes descargables en PDF

El usuario descarga dos reportes PDF generados desde el resultado persistido.

### Story 2.1: Builder común de PDF y reporte de validación de reglas de negocio

As a usuario anónimo (analista),
I want descargar un PDF con el objetivo, los usuarios finales y las reglas de negocio,
So that pueda llevarlo al cliente para confirmar la comprensión.

**Acceptance Criteria:**

**Given** un `analysis_id` con resultado persistido
**When** solicito el reporte de reglas de negocio
**Then** el sistema genera un PDF (reportlab) con objetivo, usuarios finales y reglas de negocio
**And** el PDF se arma SOLO desde el resultado persistido, sin re-leer el documento original
**And** existe un builder común reutilizable para ambos tipos de reporte
**And** un test genera el PDF desde un fixture y verifica content-type y tamaño > 0 sin invocar el parser de archivos

### Story 2.2: Reporte de validación de HUs

As a usuario anónimo,
I want descargar un PDF con la calificación por HU y la general,
So that tenga un registro del análisis de calidad.

**Acceptance Criteria:**

**Given** un `analysis_id` con resultado persistido
**When** solicito el reporte de validación de HUs
**Then** el PDF incluye, por HU, su score, banda, observaciones y sugerencias, más la calificación general
**And** reutiliza el builder común de PDF

### Story 2.3: Descarga de reportes desde el frontend

As a usuario anónimo,
I want botones para descargar cada reporte en PDF,
So that obtenga los documentos sin pasos manuales.

**Acceptance Criteria:**

**Given** la vista de resultados con un `analysis_id`
**When** hago clic en "Descargar reglas de negocio" o "Descargar validación de HUs"
**Then** el navegador descarga el PDF correspondiente vía `GET /api/v1/report/{analysis_id}?type=business|hu`
**And** si el resultado ya no está disponible en sesión, veo un mensaje claro

## Epic 3: Panel de administrador y métricas

El administrador inicia sesión y consulta uso, métricas por banda y resultados, sin acceso a documentos.

### Story 3.1: Login del administrador con JWT

As a administrador,
I want iniciar sesión con credenciales seguras,
So that acceda al panel protegido.

**Acceptance Criteria:**

**Given** `POST /api/v1/admin/login`
**When** envío la contraseña del admin
**Then** el sistema la valida contra `ADMIN_PASSWORD_HASH` (passlib/bcrypt) y devuelve un JWT firmado con expiración
**And** las rutas `/api/v1/admin/*` rechazan peticiones sin un JWT válido
**And** las credenciales y el secreto JWT provienen de `.env` y no se exponen en el cliente

### Story 3.2: Métricas de uso por periodo

As a administrador,
I want ver cuántas veces se usó la herramienta por día, semana, mes y año,
So that entienda la adopción.

**Acceptance Criteria:**

**Given** el panel admin autenticado
**When** consulto `GET /api/v1/admin/metrics`
**Then** el sistema devuelve conteos de análisis agregados por día, semana, mes y año (`GROUP BY` sobre `analysis.created_at`)
**And** los datos provienen solo de la tabla de análisis, sin identidad de usuario

### Story 3.3: Métricas por banda de calificación

As a administrador,
I want ver la distribución de análisis por banda de calificación,
So that conozca la calidad típica de los documentos.

**Acceptance Criteria:**

**Given** el panel admin autenticado
**When** consulto las métricas por banda
**Then** veo la distribución (conteo y %) por banda (Excepcional/Bueno/Regular/Crítico)
**And** las bandas se calculan en query a partir de los scores, no se almacenan

### Story 3.4: Listado de resultados de análisis sin documentos

As a administrador,
I want ver los resultados de los análisis realizados,
So that revise el desempeño sin acceder a información confidencial.

**Acceptance Criteria:**

**Given** el panel admin autenticado
**When** consulto `GET /api/v1/admin/analyses`
**Then** veo la lista de análisis con su fecha, score general, banda y estado
**And** en ningún caso se exponen los documentos subidos ni el texto extraído (no existen en persistencia)
