"""
Pruebas de los reportes PDF (Stories 2.1–2.3).

Los builders se prueban desde un fixture (sin invocar el parser de archivos) y el
endpoint genera el PDF SOLO desde el resultado persistido.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary
from app.services.pdf_generator import build_business_report, build_hu_report
from app.services.persistence import save_analysis


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client(session):
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _sample() -> AnalyzeResponse:
    return AnalyzeResponse(
        status="ok",
        story_count=1,
        hu_results=[HUResult(
            hu_id="HU-01", original_text="Como cliente quiero X para Y",
            score=78, band="Bueno", evaluated=True,
            feedback=["Falta criterio."], suggestions=["Agregar criterio."],
        )],
        project_summary=ProjectSummary(
            objective="Plataforma demo.", stakeholders=["Cliente"],
            business_rules=["Solo autenticados."],
        ),
        overall_score=78.0, overall_band="Bueno",
    )


def test_builders_return_pdf_bytes():
    for pdf in (build_business_report(_sample()), build_hu_report(_sample())):
        assert pdf[:5] == b"%PDF-"
        assert len(pdf) > 0


def test_get_report_from_persisted_result(session, client):
    analysis_id = save_analysis(session, _sample(), file_type="txt", duration_ms=1, model_version="m")
    for report_type in ("business", "hu"):
        resp = client.get(f"/api/v1/report/{analysis_id}?type={report_type}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 0


def test_get_report_unknown_returns_404(client):
    resp = client.get("/api/v1/report/no-existe?type=business")
    assert resp.status_code == 404


def test_get_report_invalid_type_returns_422(session, client):
    analysis_id = save_analysis(session, _sample(), file_type="txt", duration_ms=1, model_version="m")
    resp = client.get(f"/api/v1/report/{analysis_id}?type=foo")
    assert resp.status_code == 422
