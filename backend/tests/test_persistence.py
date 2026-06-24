"""
Pruebas de persistencia y recuperación (Story 1.9).

Verifican el roundtrip save → load y la garantía de privacidad: el texto original
del documento NUNCA se persiste (se recupera vacío).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary
from app.services.persistence import load_analysis, save_analysis


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()


def _sample_response() -> AnalyzeResponse:
    return AnalyzeResponse(
        status="ok",
        story_count=1,
        hu_results=[HUResult(
            hu_id="HU-01",
            original_text="Como cliente quiero ver el historial para revisar pedidos.",
            score=75,
            band="Bueno",
            evaluated=True,
            feedback=["Falta criterio de paginación."],
            suggestions=["Agregar criterio de paginación."],
        )],
        project_summary=ProjectSummary(
            objective="Plataforma de gestión de compras.",
            stakeholders=["Cliente"],
            business_rules=["Solo usuarios autenticados acceden al historial."],
        ),
        overall_score=75.0,
        overall_band="Bueno",
    )


def test_save_and_load_roundtrip(db):
    analysis_id = save_analysis(
        db, _sample_response(), file_type="txt", duration_ms=1200, model_version="gpt-4o-mini",
    )
    assert analysis_id

    loaded = load_analysis(db, analysis_id)
    assert loaded is not None
    assert loaded.analysis_id == analysis_id
    assert loaded.status == "ok"
    assert loaded.overall_band == "Bueno"
    assert len(loaded.hu_results) == 1
    hu = loaded.hu_results[0]
    assert hu.score == 75
    assert hu.band == "Bueno"
    assert "Falta criterio de paginación." in hu.feedback
    assert loaded.project_summary.objective == "Plataforma de gestión de compras."
    assert loaded.project_summary.stakeholders == ["Cliente"]


def test_original_text_is_never_persisted(db):
    analysis_id = save_analysis(
        db, _sample_response(), file_type="txt", duration_ms=0, model_version="m",
    )
    loaded = load_analysis(db, analysis_id)
    # El texto del documento no se almacena; se recupera vacío.
    assert loaded.hu_results[0].original_text == ""


def test_load_missing_returns_none(db):
    assert load_analysis(db, "no-existe") is None
