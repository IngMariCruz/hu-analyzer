---
title: PRD — HU Analyzer (v1)
status: final
created: 2026-06-23
updated: 2026-06-23
---

# HU Analyzer — PRD (v1)

## 1. Visión y problema

Las empresas gastan muchas iteraciones y reuniones para levantar requisitos y validarlos con el cliente. Gran parte de ese esfuerzo se va en confirmar que lo escrito refleja lo que el cliente realmente quiere.

**HU Analyzer** ayuda al **analista/consultor** a acortar ese ciclo. Recibe un documento con Historias de Usuario (HU), evalúa su calidad con un LLM y —sobre todo— **infiere y devuelve el objetivo del proyecto, los usuarios finales y las reglas de negocio** para que el analista confirme con el cliente que entendió bien su idea, reduciendo reuniones e iteraciones.

**Diferenciador:** el reporte de **validación de reglas de negocio**. No es feedback de redacción; es "esto es lo que entendí de tu negocio, confírmalo".

## 2. Objetivos y métricas de éxito

**Objetivos**
- Dar al analista una evaluación objetiva de la calidad de sus HUs antes de pasarlas a desarrollo.
- Producir un artefacto (reporte de reglas de negocio) que el analista lleve al cliente para validar la comprensión del problema.
- Ofrecer la herramienta de forma gratuita y sin fricción a usuarios de internet.

**Métricas de éxito (v1 — demo/portafolio)**
- Nº de análisis completados (uso de la herramienta).
- Distribución de calificaciones por banda (señal de calidad típica de los documentos de entrada).
- Nº de reportes PDF descargados.

**Contra-métricas (señales de alarma)**
- Tasa alta de documentos marcados "no contiene proyecto" o "info no válida" → problema de parseo, segmentación o UX, no del usuario.
- Tiempo de análisis percibido como excesivo.

## 3. Usuarios y roles

- **Analista / consultor (protagonista).** Levanta requisitos y escribe las HUs. Usa la herramienta para autoevaluar calidad y para generar el reporte de reglas de negocio que valida con el cliente. Es un *usuario de internet*.
- **Usuario de internet (anónimo).** Cualquiera, sin registro. Sube HU, recibe el análisis y descarga reportes en PDF. Gratis.
- **Administrador (Mcruz).** Accede con login a un panel de métricas. Ve el uso de la herramienta y los resultados de los análisis, pero **nunca** los documentos HU subidos.

## 4. User journey — Analista

1. Llega a HU Analyzer (sin registrarse) y sube su documento de HUs (PDF/Word/TXT/Excel).
2. La herramienta extrae el texto y determina si el documento contiene un proyecto.
   - Si no → ve una alerta clara y puede subir otro documento.
   - Si sí pero la info no es válida → ve qué no se comprendió y la indicación de replantear el documento.
3. Si la info es válida, ve los resultados: calificación por HU (1–100 + banda), promedio del documento, y la inferencia de objetivo / usuarios finales / reglas de negocio.
4. Para las HUs con calificación < 90 ve sugerencias concretas de mejora.
5. Descarga el **reporte de reglas de negocio** en PDF y lo lleva al cliente para confirmar la comprensión. Opcionalmente descarga el **reporte de validación de HUs**.

## 5. Alcance

**Dentro de v1**
- Carga de un documento por análisis en PDF, Word, TXT, Excel.
- Validación de pertinencia y validez del contenido.
- Evaluación de HUs (formato, INVEST, coherencia, ambigüedad/contradicción) con calificación 1–100 y bandas.
- Inferencia de objetivo, usuarios finales y reglas de negocio.
- Sugerencias de mejora cuando la calificación < 90.
- Dos reportes descargables en PDF.
- Acceso anónimo para usuarios de internet; panel autenticado para el administrador.
- Panel de métricas de uso y calificaciones.

**Fuera de v1**
- Registro/cuentas e historial por usuario final.
- Almacenamiento de los documentos subidos.
- OCR para PDFs escaneados sin texto (deuda técnica conocida).
- Procesamiento por lotes / múltiples documentos a la vez.
- Edición colaborativa o exportación a otros formatos (Word, etc.).

## 6. Requisitos funcionales

### A. Ingesta de documentos
- **FR1** — El usuario puede subir un archivo en formato PDF, Word (.docx), TXT o Excel (.xlsx).
- **FR2** — El sistema extrae el texto del documento según su tipo de archivo.
- **FR3** — El sistema valida tipo y tamaño de archivo (límite configurable) y rechaza lo no soportado con un mensaje claro.
- **FR4** — El documento se procesa en memoria y no se almacena tras el análisis.

### B. Validación de pertinencia y validez
- **FR5** — Mediante el LLM, el sistema determina si el documento contiene información de un proyecto.
- **FR6** — Si no contiene información de un proyecto, muestra una alerta al usuario y no realiza el análisis.
- **FR7** — Si contiene un proyecto, el sistema determina si la información es válida (se comprende el core del negocio).
- **FR8** — Si la información no es válida, indica al usuario que debe replantear el contenido del documento y muestra qué no se comprendió (p. ej. falta objetivo, HUs sin contexto).
- **FR9** — Si la información es válida, el sistema procede con la evaluación y la inferencia de negocio.

### C. Evaluación de HUs
- **FR10** — El sistema segmenta el documento en HUs individuales.
- **FR11** — Por cada HU, evalúa el formato "Como / Quiero / Para".
- **FR12** — Por cada HU, evalúa los criterios de aceptación contra INVEST.
- **FR13** — Por cada HU, evalúa la coherencia interna del enunciado.
- **FR14** — El sistema detecta ambigüedades o contradicciones dentro del mismo documento.
- **FR15** — El sistema asigna a cada HU una calificación de 1 a 100.
- **FR16** — El sistema clasifica cada calificación en una banda: 90–100 Excepcional, 70–89 Bueno, 50–69 Regular, < 50 Crítico.
- **FR17** — El sistema calcula y presenta una calificación promedio del documento (promedio simple de las calificaciones de las HUs), con su banda.

### D. Inferencia de negocio
- **FR18** — El sistema infiere el objetivo del proyecto.
- **FR19** — El sistema infiere los usuarios finales del proyecto (stakeholders, solo usuarios finales).
- **FR20** — El sistema infiere las reglas de negocio.

### E. Sugerencias de mejora
- **FR21** — Para cada HU con calificación < 90, el sistema genera sugerencias concretas de cómo mejorar su calificación.

### F. Reportes en PDF
- **FR22** — El sistema genera un reporte "Validación de reglas de negocio" que contiene objetivo del proyecto, usuarios finales y reglas de negocio.
- **FR23** — El sistema genera un reporte "Validación de HUs" que contiene la calificación por HU, las observaciones, las sugerencias y la calificación general.
- **FR24** — El usuario puede descargar ambos reportes en PDF.

### G. Roles y acceso
- **FR25** — El usuario de internet usa la herramienta de forma anónima y gratuita: sube HU y descarga reportes sin registrarse.
- **FR26** — El administrador accede a su panel mediante autenticación.
- **FR27** — El administrador no puede ver los documentos HU subidos por los usuarios.

### H. Panel de métricas (administrador)
- **FR28** — El sistema registra cada uso de la herramienta (sin almacenar el documento).
- **FR29** — El panel muestra el número de usos por día, semana, mes y año.
- **FR30** — El panel muestra métricas por banda de calificación.
- **FR31** — El panel muestra los resultados de los análisis, sin los documentos asociados.

## 7. Requisitos no funcionales

- **Privacidad por diseño.** Los documentos HU no se persisten en ningún momento; solo se guardan resultados de análisis y métricas agregadas. El panel de administrador nunca expone documentos. [NOTA: esto incluye no almacenar el texto extraído más allá de lo necesario para producir el resultado de la sesión.]
- **Modelo LLM.** El análisis usa **GPT-4o mini** (OpenAI). Ante timeout, error de API o respuesta mal formada, el sistema muestra un mensaje de error claro al usuario (sin pantalla en blanco ni resultado parcial silencioso) y permite reintentar. Se muestra estado de carga durante el análisis.
- **Costos.** El documento se envía al LLM una sola vez por análisis (sin reenvíos innecesarios); el modelo económico se elige a propósito para acotar el costo por análisis.
- **Restricciones de archivo.** Tamaño máximo configurable (default 10 MB); tipos soportados PDF/.docx/.txt/.xlsx. Otros tipos o tamaños mayores se rechazan antes de procesar.
- **Idioma.** Los documentos de entrada se esperan principalmente en español; el análisis y los reportes se entregan en español.
- **Escala.** v1 es demo/portafolio: no se requiere alta concurrencia. Objetivo: el análisis de un documento típico (≤ ~15 HUs) se completa en menos de ~60 s.
- **Seguridad.** El panel de administrador requiere autenticación; las credenciales no se exponen en el cliente.

## 8. Supuestos y preguntas abiertas

- Existe un único administrador (Mcruz) con login email+contraseña. 
- Cada análisis procesa un documento a la vez.
- La calificación promedio del documento es un **promedio simple** de las calificaciones de las HUs (FR17).
- Las sugerencias de mejora se generan **solo por HU** con calificación < 90 (FR21).
- Las "métricas por banda" incluyen conteo y porcentaje por banda, con tendencia en el tiempo (día/semana/mes/año). *Default; confirmar al diseñar el panel.*
- **[RESUELTO]** v1 migra a GPT-4o mini y **elimina la dependencia de Anthropic/Claude** del flujo de análisis.
