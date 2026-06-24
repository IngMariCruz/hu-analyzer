"""
Pruebas del panel admin (Epic 3): login JWT, protección de rutas y métricas.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.security import hash_password
from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.models.schemas import AnalyzeResponse, HUResult, ProjectSummary
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
def client(session, monkeypatch):
    monkeypatch.setattr(security.settings, "ADMIN_PASSWORD_HASH", hash_password("secret"))
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_db(session, monkeypatch):
    """Cliente SIN hash en .env: fuerza el flujo de registro/login por base de datos."""
    import app.services.admin_service as admin_service
    monkeypatch.setattr(security.settings, "ADMIN_PASSWORD_HASH", "")
    monkeypatch.setattr(admin_service.settings, "ADMIN_PASSWORD_HASH", "")
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _analysis(score: float, status_value: str = "ok") -> AnalyzeResponse:
    return AnalyzeResponse(
        status=status_value, story_count=1,
        hu_results=[HUResult(hu_id="HU-01", original_text="t", score=int(score) or 1,
                             band="Bueno", evaluated=True, feedback=[], suggestions=[])],
        project_summary=ProjectSummary(objective="o", stakeholders=[], business_rules=[]),
        overall_score=score, overall_band="Bueno",
    )


def _token(client) -> str:
    resp = client.post("/api/v1/admin/login", json={"password": "secret"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_login_success_and_failure(client):
    assert client.post("/api/v1/admin/login", json={"password": "secret"}).status_code == 200
    assert client.post("/api/v1/admin/login", json={"password": "wrong"}).status_code == 401


def test_admin_routes_require_jwt(client):
    # Sin token → 401
    assert client.get("/api/v1/admin/metrics").status_code == 401
    assert client.get("/api/v1/admin/analyses").status_code == 401
    # Con token → 200
    headers = {"Authorization": f"Bearer {_token(client)}"}
    assert client.get("/api/v1/admin/metrics", headers=headers).status_code == 200


def test_band_distribution_and_listing_without_documents(session, client):
    save_analysis(session, _analysis(95), file_type="txt", duration_ms=1, model_version="m")
    save_analysis(session, _analysis(40), file_type="pdf", duration_ms=1, model_version="m")
    headers = {"Authorization": f"Bearer {_token(client)}"}

    bands = client.get("/api/v1/admin/metrics/bands", headers=headers).json()
    assert bands["total"] == 2
    by_band = {d["band"]: d["count"] for d in bands["distribution"]}
    assert by_band["Excepcional"] == 1
    assert by_band["Crítico"] == 1

    analyses = client.get("/api/v1/admin/analyses", headers=headers).json()
    assert len(analyses) == 2
    assert "band" in analyses[0] and "status" in analyses[0]
    # Privacidad: el listado nunca expone documentos ni texto extraído.
    assert "original_text" not in str(analyses)


def test_invalid_token_rejected(client):
    headers = {"Authorization": "Bearer not-a-jwt"}
    assert client.get("/api/v1/admin/metrics", headers=headers).status_code == 401


# ── Registro de primer uso (DB) ──────────────────────────────────────────────

def test_register_then_exists_and_login(client_db):
    # Sin admin: exists=False
    assert client_db.get("/api/v1/admin/exists").json()["registered"] is False

    # Registro de primer uso → token
    resp = client_db.post("/api/v1/admin/register", json={"username": "mary", "password": "secreto123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert client_db.get("/api/v1/admin/metrics", headers={"Authorization": f"Bearer {token}"}).status_code == 200

    # Ahora exists=True
    assert client_db.get("/api/v1/admin/exists").json()["registered"] is True

    # Login con el usuario registrado
    ok = client_db.post("/api/v1/admin/login", json={"username": "mary", "password": "secreto123"})
    assert ok.status_code == 200
    # Contraseña/usuario incorrectos → 401
    assert client_db.post("/api/v1/admin/login", json={"username": "mary", "password": "mala"}).status_code == 401
    assert client_db.post("/api/v1/admin/login", json={"username": "otra", "password": "secreto123"}).status_code == 401


def test_register_blocked_when_admin_exists(client_db):
    client_db.post("/api/v1/admin/register", json={"username": "mary", "password": "secreto123"})
    # Segundo registro bloqueado
    resp = client_db.post("/api/v1/admin/register", json={"username": "otro", "password": "secreto123"})
    assert resp.status_code == 409
