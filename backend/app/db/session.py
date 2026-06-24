"""
Sesión y motor SQLAlchemy (SQLite). Engine síncrono: las escrituras son pequeñas
y SQLite es local; aceptable para la escala demo/portafolio.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base

# `check_same_thread=False`: FastAPI puede atender la request en otro hilo.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Crea el esquema inicial si no existe (sin Alembic en la demo)."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Dependencia FastAPI: una sesión por request, cerrada al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
