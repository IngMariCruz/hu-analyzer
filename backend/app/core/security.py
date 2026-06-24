"""
Seguridad del panel admin (Story 3.1).

Password hasheado (passlib/bcrypt) + JWT firmado (pyjwt) con expiración. El
secreto y el hash provienen de `.env`; nunca se exponen en el cliente. La
dependencia `require_admin` protege las rutas `/api/v1/admin/*`.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)

# bcrypt opera sobre bytes y trunca a 72 bytes; lo hacemos explícito.
def _to_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Genera un hash bcrypt (utilidad para crear `ADMIN_PASSWORD_HASH`)."""
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str) -> bool:
    """Verifica la contraseña contra `ADMIN_PASSWORD_HASH`."""
    if not settings.ADMIN_PASSWORD_HASH:
        return False
    try:
        return bcrypt.checkpw(_to_bytes(password), settings.ADMIN_PASSWORD_HASH.encode("utf-8"))
    except ValueError:
        # Hash mal formado en .env
        return False


def create_access_token(subject: str = "admin") -> str:
    """Crea un JWT firmado con expiración para la sesión admin."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """Dependencia FastAPI: rechaza si falta o es inválido el JWT de admin."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub", "admin")
