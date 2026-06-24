---
title: 'Story 3.5 (añadida) — Frontend del panel admin con registro y login'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
Interfaz del panel admin en el frontend: registro de primer uso, login y dashboard de métricas. (No existía en el plan; el admin se autenticaba solo por hash en `.env`.)

## Resultado
**Backend:** tabla `admin_user` (`db/models.py`) + `services/admin_service.py` (`admin_exists`, `register_admin` bootstrap-only, `authenticate` con respaldo al hash de `.env`). Endpoints en `routes/admin.py`: `GET /admin/exists`, `POST /admin/register` (409 si ya hay admin), `POST /admin/login` ahora acepta `{username, password}`. `create_access_token(subject)` parametrizado.

**Frontend:** `react-router-dom` v7; `App.jsx` enruta `/` (`AnalyzerPage`) y `/admin` (`AdminPage`). `services/adminApi.js` (token JWT en `localStorage`, `authFetch` con Bearer y manejo de 401). Componentes: `AdminAuth` (decide Registro/Login según `/admin/exists`, con toggle), `AdminDashboard` (uso por periodo, distribución por banda con barras, listado de análisis sin documentos). Enlace "Admin" en el header del analizador; logout y "Volver".

## Decisión de diseño
Registro **de primer uso** (solo mientras no exista admin) para mantener la privacidad por diseño sin abrir registro público. El hash de `.env` sigue funcionando como respaldo single-admin.

## Cubre
FR26 (login) + UI de FR29/FR30/FR31.

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_admin.py -q` -- expected: verde (exists/register/login + bloqueo de segundo registro).
- `cd frontend && npm run build` -- expected: build sin errores. Manual: `npm run dev` → http://localhost:5173/admin.
