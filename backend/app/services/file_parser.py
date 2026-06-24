"""
FileParser: extrae texto de archivos (.docx, .pdf, .xlsx, .txt)
y segmenta el contenido en Historias de Usuario individuales.
"""

import re
import io
from dataclasses import dataclass

import pdfplumber
import openpyxl
from docx import Document
from fastapi import UploadFile


@dataclass
class ParsedHU:
    hu_id: str
    raw_text: str


@dataclass
class ParseResult:
    hus: list[ParsedHU]
    source_type: str
    total_found: int
    raw_text: str = ""


# ── Patrones de segmentación ────────────────────────────────────────────────

# Detecta encabezados de HU en múltiples formatos:
# "HU 0.1", "HU 0.1 –", "HU 1.0 –", "HU-01", "HU01", "US-01", "1.", "Historia 1"
HU_SPLIT_PATTERN = re.compile(
    r'(?:^|\n)(?=\s*(?:'
    r'HU\s+\d+[\.\d]*'       # HU 0.1, HU 1.0, HU 4.3
    r'|HU[-]?\d+[\.\d]*'     # HU-01, HU01
    r'|US[-\s]?\d+[\.\d]*'   # US-01, US 1.0
    r'|Historia\s+de\s+Usuario\s*\d*'
    r'|\d+[.)]\s'             # 1. o 1)
    r'))',
    re.IGNORECASE | re.MULTILINE,
)

# Extrae el ID limpio de la primera línea del bloque
HU_ID_PATTERN = re.compile(
    r'^(HU\s+\d+[\.\d]*|HU[-]?\d+[\.\d]*|US[-\s]?\d+[\.\d]*|Historia\s+\d+|\d+)',
    re.IGNORECASE,
)


def _normalize_hu_id(raw_id: str) -> str:
    """Normaliza el ID extraído a formato estándar. Ej: 'HU 0.1' → 'HU-0.1'"""
    raw_id = raw_id.strip()
    # Si es solo número, convertir a HU-XX
    if re.match(r'^\d+$', raw_id):
        return f"HU-{int(raw_id):02d}"
    # Normalizar espacios a guión: "HU 0.1" → "HU-0.1"
    normalized = re.sub(r'^(HU|US)\s+', r'\1-', raw_id, flags=re.IGNORECASE)
    return normalized.upper()


# ── Parsers por tipo de archivo ─────────────────────────────────────────────

def _parse_txt(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo decodificar el archivo .txt.")


def _parse_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if para.style.name.startswith("Heading"):
            paragraphs.append(f"\n{text}")
        else:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _parse_pdf(content: bytes) -> str:
    pages = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    return "\n\n".join(pages)


def _parse_xlsx(content: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return ""

    header = [str(cell).strip().lower() if cell else "" for cell in rows[0]]
    HU_COLUMNS = {"hu", "historia", "historia de usuario", "us", "user story",
                  "descripción", "descripcion"}
    has_header = any(col in HU_COLUMNS for col in header)
    data_rows = rows[1:] if has_header else rows
    blocks = []

    for i, row in enumerate(data_rows, start=1):
        cells = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
        if not cells:
            continue
        if has_header:
            parts = [
                f"{header[j].capitalize()}: {cells[j]}"
                for j in range(min(len(header), len(cells)))
                if cells[j]
            ]
            blocks.append(f"HU-{i:02d}\n" + "\n".join(parts))
        else:
            blocks.append(f"HU-{i:02d}\n" + " ".join(cells))

    return "\n\n".join(blocks)


# ── Segmentador ─────────────────────────────────────────────────────────────

def _segment_hus(text: str, source_type: str) -> list[ParsedHU]:
    if source_type == "xlsx":
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    else:
        blocks = [b.strip() for b in HU_SPLIT_PATTERN.split(text) if b.strip()]
        if len(blocks) <= 1:
            blocks = [text.strip()]

    hus = []
    for i, block in enumerate(blocks, start=1):
        first_line = block.split("\n")[0].strip()
        id_match = HU_ID_PATTERN.match(first_line)

        if id_match:
            hu_id = _normalize_hu_id(id_match.group(1))
        else:
            hu_id = f"HU-{i:02d}"

        hus.append(ParsedHU(hu_id=hu_id, raw_text=block))

    return hus


# ── Interfaz pública ────────────────────────────────────────────────────────

CONTENT_TYPE_MAP = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "text/plain": "txt",
}


async def parse_file(file: UploadFile) -> ParseResult:
    source_type = CONTENT_TYPE_MAP.get(file.content_type)
    if not source_type:
        raise ValueError(f"Tipo de archivo no soportado: {file.content_type}")

    content = await file.read()
    if not content:
        raise ValueError("El archivo está vacío.")

    parsers = {
        "txt": _parse_txt,
        "docx": _parse_docx,
        "pdf": _parse_pdf,
        "xlsx": _parse_xlsx,
    }
    raw_text = parsers[source_type](content)

    if not raw_text.strip():
        raise ValueError("No se encontró texto en el archivo.")

    hus = _segment_hus(raw_text, source_type)

    return ParseResult(
        hus=hus,
        source_type=source_type,
        total_found=len(hus),
        raw_text=raw_text,
    )
