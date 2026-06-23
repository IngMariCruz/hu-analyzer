"""
Pruebas de extracción de texto e segmentación de HU (Stories 1.2 y 1.4).
"""

from app.services.file_parser import _parse_txt, _segment_hus


def test_parse_txt_decodes_utf8():
    assert "café" in _parse_txt("café".encode("utf-8"))


def test_parse_txt_decodes_latin1_fallback():
    # Bytes no válidos en utf-8 deben caer al fallback sin lanzar excepción.
    assert _parse_txt("ñ".encode("latin-1"))


def test_segment_multiple_hus():
    text = (
        "HU-01\nComo cliente quiero ver el historial para revisar pedidos.\n\n"
        "HU-02\nComo admin quiero exportar datos para auditar."
    )
    hus = _segment_hus(text, "txt")
    assert len(hus) == 2
    assert hus[0].hu_id == "HU-01"
    assert hus[1].hu_id == "HU-02"


def test_segment_single_block_fallback():
    hus = _segment_hus("Texto corrido sin patrón de HU reconocible.", "txt")
    assert len(hus) == 1
