"""
Panel de administrador (Epic 3): login con JWT y métricas.

Todas las rutas excepto `login` exigen un JWT válido (`require_admin`). Las
métricas operan solo sobre la tabla `analysis`, sin documentos ni identidad.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, require_admin
from app.db.session import get_db
from app.models.schemas import (
    AdminExistsResponse,
    AdminLoginRequest,
    AdminRegisterRequest,
    ErrorResponse,
    TokenResponse,
)
from app.services.admin_service import admin_exists, authenticate, register_admin
from app.services.metrics import band_distribution, list_analyses, usage_by_period

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/exists",
    summary="¿Ya hay un administrador registrado?",
    response_model=AdminExistsResponse,
)
async def exists(db: Session = Depends(get_db)):
    """Indica al frontend si mostrar Registro (primer uso) o Login."""
    return AdminExistsResponse(registered=admin_exists(db))


@router.post(
    "/register",
    summary="Registrar el administrador (solo primer uso)",
    response_model=TokenResponse,
    responses={409: {"description": "Ya existe un administrador.", "model": ErrorResponse}},
)
async def register(body: AdminRegisterRequest, db: Session = Depends(get_db)):
    """Crea el admin de primer uso y devuelve un JWT (auto-login). Bloqueado si ya existe uno."""
    try:
        admin = register_admin(db, body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return TokenResponse(access_token=create_access_token(admin.username))


@router.post(
    "/login",
    summary="Iniciar sesión del administrador",
    response_model=TokenResponse,
    responses={401: {"description": "Credenciales inválidas.", "model": ErrorResponse}},
)
async def login(body: AdminLoginRequest, db: Session = Depends(get_db)):
    """Valida usuario/contraseña (o solo contraseña vía `.env`) y devuelve un JWT."""
    subject = authenticate(db, body.username, body.password)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )
    return TokenResponse(access_token=create_access_token(subject))


@router.get(
    "/metrics",
    summary="Usos por día, semana, mes y año",
    dependencies=[Depends(require_admin)],
)
async def metrics(db: Session = Depends(get_db)):
    """Conteos de análisis agregados por periodo (FR29)."""
    return usage_by_period(db)


@router.get(
    "/metrics/bands",
    summary="Distribución por banda de calificación",
    dependencies=[Depends(require_admin)],
)
async def metrics_bands(db: Session = Depends(get_db)):
    """Distribución (conteo y %) por banda (FR30)."""
    return band_distribution(db)


@router.get(
    "/analyses",
    summary="Listado de resultados de análisis (sin documentos)",
    dependencies=[Depends(require_admin)],
)
async def analyses(db: Session = Depends(get_db)):
    """Lista de análisis con fecha, score, banda y estado (FR31)."""
    return list_analyses(db)
