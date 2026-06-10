"""
pdf_generator.py — genera el reporte PDF del análisis de HU.

Diseño:
- Portada con score global
- Resumen del proyecto (objetivo, stakeholders, reglas de negocio)
- Una sección por HU con score badge, observaciones y sugerencias
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Circle, String
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable

from app.models.schemas import AnalyzeResponse

# ── Paleta de colores ────────────────────────────────────────────────────────
VIOLET      = colors.HexColor("#7C3AED")
VIOLET_LIGHT= colors.HexColor("#EDE9FE")
VIOLET_MID  = colors.HexColor("#DDD6FE")
TEXT_DARK   = colors.HexColor("#111827")
TEXT_GRAY   = colors.HexColor("#6B7280")
TEXT_LIGHT  = colors.HexColor("#9CA3AF")
GREEN       = colors.HexColor("#059669")
GREEN_BG    = colors.HexColor("#D1FAE5")
AMBER       = colors.HexColor("#D97706")
AMBER_BG    = colors.HexColor("#FEF3C7")
RED         = colors.HexColor("#DC2626")
RED_BG      = colors.HexColor("#FEE2E2")
WHITE       = colors.white
PAGE_BG     = colors.HexColor("#FAFAF9")


def _score_color(score: float):
    if score >= 8:
        return GREEN, GREEN_BG
    if score >= 6:
        return AMBER, AMBER_BG
    return RED, RED_BG


def _score_label(score: float) -> str:
    if score >= 8:
        return "Buena"
    if score >= 6:
        return "Regular"
    return "Deficiente"


# ── Flowable: badge de score circular ───────────────────────────────────────

class ScoreBadge(Flowable):
    """Círculo con el score dibujado como Flowable de reportlab."""

    def __init__(self, score: float, size: float = 50):
        super().__init__()
        self.score = score
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        fg, bg = _score_color(self.score)
        r = self.size / 2
        cx, cy = r, r
        # Fondo del círculo
        self.canv.setFillColor(bg)
        self.canv.setStrokeColor(fg)
        self.canv.setLineWidth(2)
        self.canv.circle(cx, cy, r - 2, fill=1, stroke=1)
        # Número
        self.canv.setFillColor(fg)
        self.canv.setFont("Helvetica-Bold", self.size * 0.28)
        label = f"{self.score:.1f}"
        self.canv.drawCentredString(cx, cy - self.size * 0.08, label)


# ── Estilos ──────────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=26,
            textColor=WHITE,
            alignment=TA_CENTER,
            leading=32,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="Helvetica",
            fontSize=12,
            textColor=colors.HexColor("#DDD6FE"),
            alignment=TA_CENTER,
            leading=18,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=VIOLET,
            spaceBefore=16,
            spaceAfter=6,
        ),
        "hu_title": ParagraphStyle(
            "hu_title",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=TEXT_DARK,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT_DARK,
            leading=14,
            alignment=TA_JUSTIFY,
        ),
        "body_gray": ParagraphStyle(
            "body_gray",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT_GRAY,
            leading=13,
            alignment=TA_LEFT,
        ),
        "label": ParagraphStyle(
            "label",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=TEXT_GRAY,
            spaceAfter=3,
        ),
        "bullet_issue": ParagraphStyle(
            "bullet_issue",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=colors.HexColor("#92400E"),
            leading=12,
            leftIndent=12,
            spaceAfter=3,
        ),
        "bullet_suggestion": ParagraphStyle(
            "bullet_suggestion",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=colors.HexColor("#065F46"),
            leading=12,
            leftIndent=12,
            spaceAfter=3,
        ),
    }
    return styles


# ── Página de portada ────────────────────────────────────────────────────────

def _build_cover(story, result: AnalyzeResponse, styles):
    score = result.overall_score
    fg, _ = _score_color(score)

    # Fondo violeta simulado con una tabla de ancho completo
    cover_data = [[
        Paragraph("HU Analyzer", styles["cover_title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[17 * cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VIOLET),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(cover_table)

    sub_data = [[
        Paragraph("Reporte de Análisis de Historias de Usuario", styles["cover_sub"]),
    ]]
    sub_table = Table(sub_data, colWidths=[17 * cm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VIOLET),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 30),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.6 * cm))

    # Fecha y totales
    now = datetime.now().strftime("%d de %B de %Y")
    n_hus = len(result.hu_results)

    meta_data = [[
        Paragraph(f"Fecha: {now}", styles["body_gray"]),
        Paragraph(f"HU analizadas: {n_hus}", styles["body_gray"]),
    ]]
    meta_table = Table(meta_data, colWidths=[8.5 * cm, 8.5 * cm])
    meta_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(HRFlowable(width="100%", thickness=1, color=VIOLET_MID))
    story.append(Spacer(1, 0.8 * cm))

    # Score global grande
    score_color, score_bg = _score_color(score)
    score_data = [[
        Paragraph("Calificación general", styles["label"]),
    ], [
        Paragraph(
            f'<font color="#{_hex(score_color)}" size="40"><b>{score:.1f}</b></font>'
            f'<font color="#{_hex(TEXT_GRAY)}" size="12"> / 10</font>',
            ParagraphStyle("sc", alignment=TA_CENTER, leading=50),
        ),
    ], [
        Paragraph(_score_label(score), ParagraphStyle(
            "sl", fontName="Helvetica-Bold", fontSize=11,
            textColor=score_color, alignment=TA_CENTER,
        )),
    ]]
    score_table = Table(score_data, colWidths=[17 * cm])
    score_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (-1, -1), score_bg),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(score_table)
    story.append(PageBreak())


def _hex(color) -> str:
    """Convierte color de reportlab a hex sin #."""
    h = color.hexval()
    return h.lstrip("#") if h.startswith("#") else h


# ── Resumen del proyecto ─────────────────────────────────────────────────────

def _build_project_summary(story, result: AnalyzeResponse, styles):
    story.append(Paragraph("Resumen del Proyecto", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VIOLET_MID))
    story.append(Spacer(1, 0.3 * cm))

    summary = result.project_summary

    # Objetivo
    obj_data = [[
        Paragraph("OBJETIVO", styles["label"]),
    ], [
        Paragraph(summary.objective, styles["body"]),
    ]]
    obj_table = Table(obj_data, colWidths=[17 * cm])
    obj_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VIOLET_LIGHT),
        ("BACKGROUND", (0, 1), (-1, 1), WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, VIOLET_MID),
    ]))
    story.append(obj_table)
    story.append(Spacer(1, 0.4 * cm))

    # Stakeholders y reglas en dos columnas
    stk_items = "\n".join(f"• {s}" for s in summary.stakeholders) or "No identificados"
    rul_items = "\n".join(f"• {r}" for r in summary.business_rules) or "No identificadas"

    two_col = [[
        [
            Paragraph("STAKEHOLDERS", styles["label"]),
            Paragraph(stk_items, styles["body"]),
        ],
        [
            Paragraph("REGLAS DE NEGOCIO", styles["label"]),
            Paragraph(rul_items, styles["body"]),
        ],
    ]]
    two_table = Table(two_col, colWidths=[8.3 * cm, 8.3 * cm], rowHeights=None)
    two_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (0, 0), 0.5, VIOLET_MID),
        ("BOX", (1, 0), (1, 0), 0.5, VIOLET_MID),
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
    ]))
    story.append(two_table)
    story.append(PageBreak())


# ── Sección por HU ───────────────────────────────────────────────────────────

def _build_hu_section(story, hu, styles):
    score_fg, score_bg = _score_color(hu.score)

    # Encabezado HU: ID + score badge inline
    header_data = [[
        Paragraph(hu.hu_id, ParagraphStyle(
            "hu_id", fontName="Helvetica-Bold", fontSize=10,
            textColor=WHITE,
        )),
        Paragraph(
            f'<b>{hu.score:.1f}</b> — {_score_label(hu.score)}',
            ParagraphStyle("hu_sc", fontName="Helvetica-Bold", fontSize=10,
                           textColor=score_fg, alignment=TA_CENTER),
        ),
    ]]
    header_table = Table(header_data, colWidths=[10 * cm, 7 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), VIOLET),
        ("BACKGROUND", (1, 0), (1, 0), score_bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Texto original
    original = hu.original_text[:400] + "..." if len(hu.original_text) > 400 else hu.original_text
    original_clean = original.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    original_data = [[
        Paragraph("TEXTO ORIGINAL", styles["label"]),
    ], [
        Paragraph(original_clean, styles["body_gray"]),
    ]]
    original_table = Table(original_data, colWidths=[17 * cm])
    original_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F9FAFB")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F9FAFB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
    ]))

    elements = [header_table, Spacer(1, 0.15 * cm), original_table]

    # Observaciones
    if hu.feedback:
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(Paragraph("OBSERVACIONES", styles["label"]))
        for item in hu.feedback:
            safe = item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.append(Paragraph(f"⚠  {safe}", styles["bullet_issue"]))

    # Sugerencias
    if hu.suggestions:
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(Paragraph("SUGERENCIAS", styles["label"]))
        for item in hu.suggestions:
            safe = item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.append(Paragraph(f"✓  {safe}", styles["bullet_suggestion"]))

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=VIOLET_MID))
    elements.append(Spacer(1, 0.3 * cm))

    story.append(KeepTogether(elements))


# ── Función principal ────────────────────────────────────────────────────────

def generate_pdf(result: AnalyzeResponse) -> bytes:
    """
    Genera el reporte PDF completo a partir de un AnalyzeResponse.
    Retorna los bytes del PDF.
    """
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Reporte HU Analyzer",
        author="HU Analyzer",
    )

    story = []

    # Portada
    _build_cover(story, result, styles)

    # Resumen del proyecto
    _build_project_summary(story, result, styles)

    # Sección por HU
    story.append(Paragraph("Análisis por Historia de Usuario", styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VIOLET_MID))
    story.append(Spacer(1, 0.4 * cm))

    for hu in result.hu_results:
        _build_hu_section(story, hu, styles)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
