"""
Modelos ORM SIN identidad (Story 1.9).

Privacidad por diseño: nunca se persiste el documento ni el texto extraído ni
PII. No hay user_id, IP, sesión ni email. Las bandas se calculan en query (no se
almacenan). `business_inference` guarda solo inferencias abstraídas (NFR de
minimización).
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    """Un análisis (también sirve como evento de uso, FR28)."""
    __tablename__ = "analysis"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    story_count: Mapped[int] = mapped_column(Integer, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    model_version: Mapped[str] = mapped_column(String, default="")
    file_type: Mapped[str] = mapped_column(String, default="")

    story_results: Mapped[list["StoryResult"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan",
    )
    business_inference: Mapped["BusinessInference | None"] = relationship(
        back_populates="analysis", cascade="all, delete-orphan", uselist=False,
    )


class StoryResult(Base):
    """Resultado por HU. NO almacena `original_text` (es texto del documento)."""
    __tablename__ = "story_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis.id"), index=True)
    hu_index: Mapped[int] = mapped_column(Integer)
    hu_id: Mapped[str] = mapped_column(String)
    score: Mapped[int] = mapped_column(Integer)
    evaluated: Mapped[bool] = mapped_column(Boolean, default=True)
    feedback: Mapped[list] = mapped_column(JSON, default=list)
    suggestions: Mapped[list] = mapped_column(JSON, default=list)

    analysis: Mapped["Analysis"] = relationship(back_populates="story_results")


class AdminUser(Base):
    """Cuenta de administrador del panel (Epic 3 — registro/login).

    Es la ÚNICA tabla con credenciales y no guarda datos de los usuarios anónimos
    ni documentos. El registro es de primer uso (bootstrap): solo se permite
    crear un admin mientras no exista ninguno.
    """
    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class BusinessInference(Base):
    """Inferencia de negocio abstraída (sin verbatim ni PII)."""
    __tablename__ = "business_inference"

    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis.id"), primary_key=True)
    objective: Mapped[str] = mapped_column(String, default="")
    end_users: Mapped[list] = mapped_column(JSON, default=list)
    business_rules: Mapped[list] = mapped_column(JSON, default=list)

    analysis: Mapped["Analysis"] = relationship(back_populates="business_inference")
