---
title: 'Story 3.1 — Login del administrador con JWT'
type: 'feature'
created: '2026-06-24'
status: 'done'
---

## Intent
`POST /api/v1/admin/login` valida la contraseña contra `ADMIN_PASSWORD_HASH` (bcrypt) y devuelve un JWT firmado con expiración; las rutas `/api/v1/admin/*` rechazan peticiones sin JWT válido. Secreto y hash desde `.env`, nunca en el cliente.

## Resultado
Nuevo `app/core/security.py`: `hash_password`/`verify_password` con la librería **bcrypt directa** (passlib 1.7.4 es incompatible con bcrypt 4.x), `create_access_token` (pyjwt HS256 + `JWT_EXPIRE_MINUTES`) y la dependencia `require_admin` (HTTPBearer → decode → 401). Route `admin.py` con `POST /admin/login` (→ `TokenResponse`) y rutas protegidas con `Depends(require_admin)`. Config: `ADMIN_PASSWORD_HASH`, `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`. Schemas `AdminLoginRequest`/`TokenResponse`.

## Cubre
FR26 (+ NFR8 credenciales fuera del cliente).

## Verification
- `cd backend && ../.venv/Scripts/python.exe -m pytest tests/test_admin.py -q` -- expected: verde (login ok/401, rutas exigen JWT, token inválido → 401).
