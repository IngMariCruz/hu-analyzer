"""
Capa de agregación de scoring (Story 1.6).

Único lugar donde viven la normalización de score (escala interna 1–10 → 1–100)
y la definición de bandas. Los checkers Strategy solo puntúan su sección (0–10);
aquí se pondera, se normaliza a 1–100 y se clasifica en banda. Si la escala o las
bandas cambian, se cambian aquí y en ningún otro sitio.
"""

from app.services.modules import ACTIVE_MODULES

# ── Bandas de calificación (1–100) ──────────────────────────────────────────
# Orden de mayor a menor; cada tupla es (mínimo inclusivo, etiqueta).
BANDS: list[tuple[int, str]] = [
    (90, "Excepcional"),
    (70, "Bueno"),
    (50, "Regular"),
    (0, "Crítico"),
]


def band_for(score: float) -> str:
    """Devuelve la banda correspondiente a un score en [0,100]."""
    for minimum, label in BANDS:
        if score >= minimum:
            return label
    return BANDS[-1][1]


def normalize_to_100(score_0_10: float) -> int:
    """Convierte un score en escala interna 0–10 a la escala pública 1–100."""
    value = round(score_0_10 * 10)
    return max(1, min(100, value))


def aggregate_hu_score(module_data: dict[str, dict]) -> int:
    """Pondera los scores 0–10 de cada módulo y normaliza a 1–100.

    Args:
        module_data: mapa `response_key -> {"score": float, ...}` con los
            puntajes 0–10 que devolvió el LLM por cada criterio.

    Returns:
        Score entero en [1,100].
    """
    total = 0.0
    total_weight = 0.0
    for module in ACTIVE_MODULES:
        data = module_data.get(module.response_key, {})
        score = float(data.get("score", 5.0))
        total += score * module.weight
        total_weight += module.weight

    weighted_0_10 = total / total_weight if total_weight else 5.0
    return normalize_to_100(weighted_0_10)


def overall_average(scores: list[float]) -> float:
    """Promedio simple del documento (0 si no hay HU evaluadas)."""
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 1)
