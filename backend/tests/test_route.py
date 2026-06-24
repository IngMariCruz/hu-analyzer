"""
Pruebas del endpoint /analyze: topes de archivo antes del LLM y wiring del
rate-limiter (Story 1.11). No invocan el LLM (los rechazos ocurren antes).
"""

import io

from fastapi.testclient import TestClient

from app.api.v1.routes import analyze as analyze_route
from app.main import app

client = TestClient(app)


def test_unsupported_file_type_rejected_before_llm():
    resp = client.post(
        "/api/v1/analyze",
        files={"file": ("x.zip", io.BytesIO(b"data"), "application/zip")},
    )
    assert resp.status_code == 422


def test_oversized_file_rejected_before_llm(monkeypatch):
    monkeypatch.setattr(analyze_route.settings, "MAX_FILE_SIZE_MB", 0)
    resp = client.post(
        "/api/v1/analyze",
        files={"file": ("x.txt", io.BytesIO(b"contenido"), "text/plain")},
    )
    assert resp.status_code == 413


def test_rate_limiter_is_wired():
    # El limiter efímero está montado en la app (Story 1.11).
    assert getattr(app.state, "limiter", None) is not None


def test_get_unknown_analysis_returns_404():
    resp = client.get("/api/v1/analyze/no-existe-id")
    assert resp.status_code == 404
