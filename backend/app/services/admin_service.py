"""
Servicio de cuentas de administrador (Epic 3 — registro/login).

Registro de primer uso (bootstrap): solo se puede crear un admin mientras no
exista ninguno en la base. El login valida contra la tabla `admin_user` y, como
respaldo, contra `ADMIN_PASSWORD_HASH` del `.env` (modo single-admin previo).
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.db.models import AdminUser


def admin_count(db: Session) -> int:
    """Número de administradores registrados en la base."""
    return db.execute(select(func.count()).select_from(AdminUser)).scalar_one()


def admin_exists(db: Session) -> bool:
    """True si ya hay un admin (en base o vía `ADMIN_PASSWORD_HASH`)."""
    return admin_count(db) > 0 or bool(settings.ADMIN_PASSWORD_HASH)


def register_admin(db: Session, username: str, password: str) -> AdminUser:
    """Crea el admin de primer uso.

    Raises:
        ValueError: si ya existe un admin (registro bloqueado) o faltan datos.
    """
    username = (username or "").strip()
    if not username or not password:
        raise ValueError("Usuario y contraseña son obligatorios.")
    if admin_count(db) > 0:
        raise ValueError("Ya existe un administrador registrado.")

    admin = AdminUser(username=username, password_hash=hash_password(password))
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def authenticate(db: Session, username: str | None, password: str) -> str | None:
    """Valida credenciales y devuelve el `subject` para el JWT, o None.

    - Si hay admins en base: valida contra el usuario indicado.
    - Si no hay admins pero existe `ADMIN_PASSWORD_HASH`: valida solo la
      contraseña (compatibilidad con el esquema single-admin del `.env`).
    """
    if admin_count(db) > 0:
        if not username:
            return None
        admin = db.execute(
            select(AdminUser).where(AdminUser.username == username.strip())
        ).scalar_one_or_none()
        if admin is None:
            return None
        return admin.username if _verify(password, admin.password_hash) else None

    # Respaldo: hash del .env (sin usuario).
    if settings.ADMIN_PASSWORD_HASH and verify_password(password):
        return "admin"
    return None


def _verify(password: str, password_hash: str) -> bool:
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], password_hash.encode("utf-8"))
    except ValueError:
        return False
