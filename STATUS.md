# HU Analyzer — Estado del proyecto

> Tablero de una página. Actualizar al cerrar cada story.
> **Última actualización:** 2026-06-24 (los 3 epics completos — 18/18 stories)

---

## Resumen

- **Versión:** v1 (demo/portafolio) — **funcionalmente completa**
- **Stack:** FastAPI + React/Vite/Tailwind · LLM: OpenAI GPT-4o mini · SQLite/SQLAlchemy
- **Progreso:** **18 / 18 stories** ✅ (Epics 1, 2 y 3 completos)
- **Tests:** 30 verdes (`backend/`)
- **Rama actual:** `feature/story-1-1-llm-provider`

---

## Tablero de stories

Leyenda: ✅ hecho · 🔜 siguiente · ⬜ pendiente

### Epic 1 — Motor de análisis de HUs
| # | Story | Estado |
|---|-------|--------|
| 1.1 | Abstracción `LLMProvider` + migración a GPT-4o mini | ✅ |
| 1.2 | Subida y extracción de texto en memoria | ✅ |
| 1.3 | Gate de pertinencia y validez del documento | ✅ |
| 1.4 | Segmentación del documento en HUs | ✅ |
| 1.5 | Evaluación por HU (formato, INVEST, coherencia, ambigüedad) | ✅ |
| 1.6 | Calificación 1–100, bandas y promedio | ✅ |
| 1.7 | Sugerencias de mejora por HU | ✅ |
| 1.8 | Inferencia de negocio con minimización | ✅ |
| 1.9 | Persistencia del resultado y recuperación por `analysis_id` | ✅ |
| 1.10 | Visualización de resultados en el frontend | ✅ |
| 1.11 | Endurecimiento — rate-limiting y topes de archivo | ✅ |

### Epic 2 — Reportes descargables en PDF
| # | Story | Estado |
|---|-------|--------|
| 2.1 | Builder común + reporte de reglas de negocio | ✅ |
| 2.2 | Reporte de validación de HUs | ✅ |
| 2.3 | Descarga de reportes desde el frontend | ✅ |

### Epic 3 — Panel de administrador y métricas
| # | Story | Estado |
|---|-------|--------|
| 3.1 | Login del administrador con JWT | ✅ |
| 3.2 | Métricas de uso por periodo | ✅ |
| 3.3 | Métricas por banda de calificación | ✅ |
| 3.4 | Listado de resultados sin documentos | ✅ |

---

## Cómo correr

```bash
# Backend (terminal 1)
cd backend
cp .env.example .env        # editar .env y poner OPENAI_API_KEY real
../.venv/Scripts/python.exe -m uvicorn app.main:app --reload
# → http://localhost:8000/docs

# Frontend (terminal 2)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

> Escala de score: **1–100** con bandas (Excepcional/Bueno/Regular/Crítico). Análisis con orquestación híbrida (1 llamada por HU + 1 de inferencia), gate de pertinencia/validez, persistencia SQLite sin identidad (`analysis_id` opaco) y rate-limiting por IP. Reportes PDF (`?type=business|hu`) desde el resultado persistido y panel admin con JWT operativos.
> La base de datos local `backend/hu_analyzer.db` se crea sola al arrancar (ignorada en git).

### Endpoints
| Método | Ruta | Auth | Para |
|--------|------|------|------|
| POST | `/api/v1/analyze` | — (rate-limit) | Subir y analizar documento |
| GET | `/api/v1/analyze/{id}` | — | Recuperar resultado por `analysis_id` |
| GET | `/api/v1/report/{id}?type=business\|hu` | — | Descargar reporte PDF |
| GET | `/api/v1/admin/exists` | — | ¿Hay admin? (decide Registro vs Login) |
| POST | `/api/v1/admin/register` | — | Registro de primer uso (bloqueado si ya existe) |
| POST | `/api/v1/admin/login` | — | Obtener JWT admin (`{username, password}`) |
| GET | `/api/v1/admin/metrics` | JWT | Usos por día/semana/mes/año |
| GET | `/api/v1/admin/metrics/bands` | JWT | Distribución por banda |
| GET | `/api/v1/admin/analyses` | JWT | Listado de análisis (sin documentos) |

> **Panel admin (frontend):** ruta **`/admin`** (http://localhost:5173/admin). En el primer uso muestra **Registro** (crea el admin en la base); luego **Login**. El JWT se guarda en `localStorage`. Alternativa sin registro: poner un hash en `ADMIN_PASSWORD_HASH` (+ `JWT_SECRET`) en `.env` con `python -c "from app.core.security import hash_password; print(hash_password('TU_PASSWORD'))"`.

## Verificar / ver estado

```bash
# Tests del backend
cd backend && ../.venv/Scripts/python.exe -m pytest -q

# Estado de stories y código
grep -E "status:|title:" _bmad-output/implementation-artifacts/spec-*.md
git log --oneline -5
git status --short
```

## Loop de desarrollo

1. Pedir una story → se implementa con `bmad-quick-dev` (spec → código → test → commit).
2. Aprobar el spec corto.
3. Correr `uvicorn` / `vite` y ver el cambio.
4. Marcar la story en este tablero y repetir.

---

## Referencias (solo si hace falta)

- PRD: [_bmad-output/planning-artifacts/prds/prd-hu-analyzer-2026-06-23/prd.md](_bmad-output/planning-artifacts/prds/prd-hu-analyzer-2026-06-23/prd.md)
- Arquitectura: [_bmad-output/planning-artifacts/architecture.md](_bmad-output/planning-artifacts/architecture.md)
- Epics y stories: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md)
- Specs por story: [_bmad-output/implementation-artifacts/](_bmad-output/implementation-artifacts/)
