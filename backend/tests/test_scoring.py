"""Pruebas de la capa de scoring centralizada (Story 1.6)."""

from app.services.scoring import (
    aggregate_hu_score,
    band_for,
    normalize_to_100,
    overall_average,
)


def test_band_thresholds():
    assert band_for(95) == "Excepcional"
    assert band_for(90) == "Excepcional"
    assert band_for(89) == "Bueno"
    assert band_for(70) == "Bueno"
    assert band_for(50) == "Regular"
    assert band_for(49) == "Crítico"
    assert band_for(0) == "Crítico"


def test_normalize_clamps_to_1_100():
    assert normalize_to_100(0) == 1
    assert normalize_to_100(10) == 100
    assert normalize_to_100(7.5) == 75
    assert 1 <= normalize_to_100(-5) <= 100


def test_aggregate_weighted_score_in_range():
    module_data = {
        "format": {"score": 8.0},
        "invest": {"score": 6.0},
        "user": {"score": 7.0},
        "functionality": {"score": 5.0},
        "coherence": {"score": 9.0},
    }
    score = aggregate_hu_score(module_data)
    assert 1 <= score <= 100
    assert isinstance(score, int)


def test_overall_average_empty_is_zero():
    assert overall_average([]) == 0.0
    assert overall_average([80, 60]) == 70.0
