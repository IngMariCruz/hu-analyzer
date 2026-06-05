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


# ── Modelo de salida ────────────────────────────────────────────────────────

@dataclass
class ParsedHU:
    """Representa una Historia de Usuario extraída del archivo."""
    hu_id: str
    raw_text: str


@dataclass
class ParseResult:
    """Resultado completo del parseo de un archivo."""
    hus: list[ParsedHU]
    source_type: str   # "docx" | "pdf" | "xlsx" | "txt"
    total_found: int


# ── Patrones de segmentación ────────────────────────────────────────────────

# Detecta inicios de HU: "HU-01", "HU01", "HU 01", "1.", "Historia 1", etc.
HU_SPLIT_PATTERN = re.compile(
    r'(?:^|\n)(?=\s*(?:HU[-\s]?\d+|Historia\s+de\s+Usuario\s*\d*|US[-\s]?\d+|\d+[.)]\s))',
    re.IGNORECASE | re.MULTILINE,
)

# Extrae el ID de una HU desde la primera línea del bloque
HU_ID_PATTERN = re.compile(
    r'^(HU[-\s]?\d+|US[-\s]?\d+|Historia\s+\d+|\d+)',
    re.IGNORECASE,
)


# ── Parsers por tipo de archivo ─────────────────────────────────────────────

def _parse_txt(content: bytes) -> str:
    """Extrae texto plano del contenido de un archivo .txt."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo decodificar el archivo .txt con las codificaciones soportadas.")


def _parse_docx(content: bytes) -> str:
    """Extrae texto de un archivo .docx conservando estructura de párrafos."""
    doc = Document(io.BytesIO(content))
    paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Marcar headings para ayudar a la segmentación
        if para.style.name.startswith("Heading"):
            paragraphs.append(f"\n{text}")
        else:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def _parse_pdf(content: bytes) -> str:
    """Extrae texto de un archivo .pdf página por página."""
    pages = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    return "\n\n".join(pages)


def _parse_xlsx(content: bytes) -> str:
    """
    Extrae HU de un archivo .xlsx.
    Asume que cada fila con contenido representa una HU o parte de ella.
    Detecta automáticamente si hay columnas con encabezados relevantes.
    """
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return ""

    # Detectar si la primera fila es encabezado
    header = [str(cell).strip().lower() if cell else "" for cell in rows[0]]
    HU_COLUMNS = {"hu", "historia", "historia de usuario", "us", "user story", "descripción", "descripcion"}
    has_header = any(col in HU_COLUMNS for col in header)

    data_rows = rows[1:] if has_header else rows
    blocks = []

    for i, row in enumerate(data_rows, start=1):
        cells = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
        if not cells:
            continue
        # Si hay encabezados, formatear como "Columna: Valor"
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


# ── Segmentador de HU ───────────────────────────────────────────────────────

def _segment_hus(text: str, source_type: str) -> list[ParsedHU]:
    """
    Divide el texto extraído en bloques individuales de HU.
    Si el texto ya viene estructurado (xlsx), retorna bloques separados por doble salto.
    De lo contrario, intenta detectar patrones de inicio de HU.
    """
    if source_type == "xlsx":
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    else:
        # Intentar dividir por patrones de HU
        blocks = [b.strip() for b in HU_SPLIT_PATTERN.split(text) if b.strip()]
        # Si no encontró patrones, tratar el documento completo como una HU
        if len(blocks) <= 1:
            blocks = [text.strip()]

    hus = []
    for i, block in enumerate(blocks, start=1):
        # Intentar extraer un ID del texto del bloque
        first_line = block.split("\n")[0].strip()
        id_match = HU_ID_PATTERN.match(first_line)

        if id_match:
            hu_id = id_match.group(1).upper().replace(" ", "-")
            # Normalizar: "1" → "HU-01"
            if hu_id.isdigit():
                hu_id = f"HU-{int(hu_id):02d}"
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
    """
    Punto de entrada principal. Lee el archivo, extrae su texto
    y lo segmenta en Historias de Usuario individuales.

    Args:
        file: Archivo subido via FastAPI UploadFile.

    Returns:
        ParseResult con la lista de HU encontradas.

    Raises:
        ValueError: Si el tipo de archivo no es soportado o el contenido está vacío.
    """
    source_type = CONTENT_TYPE_MAP.get(file.content_type)
    if not source_type:
        raise ValueError(f"Tipo de archivo no soportado: {file.content_type}")

    content = await file.read()
    if not content:
        raise ValueError("El archivo está vacío.")

    # Extraer texto según tipo
    parsers = {
        "txt": _parse_txt,
        "docx": _parse_docx,
        "pdf": _parse_pdf,
        "xlsx": _parse_xlsx,
    }
    raw_text = parsers[source_type](content)

    if not raw_text.strip():
        raise ValueError("No se encontró texto en el archivo.")

    # Segmentar en HU individuales
    hus = _segment_hus(raw_text, source_type)

    return ParseResult(
        hus=hus,
        source_type=source_type,
        total_found=len(hus),
    )
