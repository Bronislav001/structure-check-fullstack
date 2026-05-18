from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader

from ..errors import ApiError


def extract_text_from_bytes(content: bytes, *, content_type: str, original_name: str = '') -> str:
    ct = str(content_type or '').lower()
    name = str(original_name or '').lower()

    try:
        if ct in {'text/plain', 'text/markdown'} or name.endswith(('.txt', '.md')):
            text = content.decode('utf-8', errors='ignore').strip()
            if not text:
                raise ApiError(400, 'FILE_PARSE_ERROR', 'text file is empty')
            return text

        if ct == 'application/pdf' or name.endswith('.pdf'):
            return _extract_pdf_text(content)

        if ct == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or name.endswith('.docx'):
            return _extract_docx_text(content)
    except ApiError:
        raise
    except Exception as exc:
        raise ApiError(400, 'FILE_PARSE_ERROR', 'failed to parse uploaded file') from exc

    raise ApiError(400, 'VALIDATION_ERROR', 'unsupported file type for text extraction')


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or '')
        except Exception:
            parts.append('')
    text = '\n'.join(parts).strip()
    if not text:
        raise ApiError(400, 'FILE_PARSE_ERROR', 'pdf text was not extracted')
    return text


def _extract_docx_text(content: bytes) -> str:
    doc = Document(BytesIO(content))
    parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text and paragraph.text.strip()]
    text = '\n'.join(parts).strip()
    if not text:
        raise ApiError(400, 'FILE_PARSE_ERROR', 'docx text was not extracted')
    return text
