"""
Consultas de métricas para el panel admin (Stories 3.2–3.4).

Operan SOLO sobre la tabla `analysis` (sin identidad de usuario ni documentos).
Las bandas se calculan en lectura a partir de los scores; no se almacenan.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Analysis
from app.services.scoring import BANDS, band_for

# Estados que aportan un score con significado para la distribución por banda.
_SCORED_STATUSES = ("ok", "partial")


def _counts_by(db: Session, fmt: str) -> list[dict]:
    """Conteo de análisis agrupado por un formato de fecha (`strftime`)."""
    bucket = func.strftime(fmt, Analysis.created_at)
    rows = db.execute(
        select(bucket.label("period"), func.count().label("count"))
        .group_by(bucket)
        .order_by(bucket)
    ).all()
    return [{"period": period, "count": count} for period, count in rows]


def usage_by_period(db: Session) -> dict[str, list[dict]]:
    """Usos por día, semana, mes y año (FR29) — `GROUP BY` sobre `created_at`."""
    return {
        "by_day": _counts_by(db, "%Y-%m-%d"),
        "by_week": _counts_by(db, "%Y-%W"),
        "by_month": _counts_by(db, "%Y-%m"),
        "by_year": _counts_by(db, "%Y"),
    }


def band_distribution(db: Session) -> dict:
    """Distribución (conteo y %) por banda de calificación (FR30).

    Bandas calculadas en lectura desde `overall_score`; solo análisis con score.
    """
    scores = db.execute(
        select(Analysis.overall_score).where(Analysis.status.in_(_SCORED_STATUSES))
    ).scalars().all()

    counts = {label: 0 for _, label in BANDS}
    for score in scores:
        counts[band_for(score)] += 1

    total = len(scores)
    distribution = [
        {
            "band": label,
            "count": counts[label],
            "percentage": round(counts[label] / total * 100, 1) if total else 0.0,
        }
        for _, label in BANDS
    ]
    return {"total": total, "distribution": distribution}


def list_analyses(db: Session, limit: int = 100) -> list[dict]:
    """Lista de análisis (FR31): fecha, score general, banda y estado.

    Nunca expone documentos ni texto extraído (no existen en persistencia).
    """
    rows = db.execute(
        select(Analysis).order_by(Analysis.created_at.desc()).limit(limit)
    ).scalars().all()
    return [
        {
            "analysis_id": a.id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "status": a.status,
            "story_count": a.story_count,
            "overall_score": a.overall_score,
            "band": band_for(a.overall_score),
            "file_type": a.file_type,
        }
        for a in rows
    ]
