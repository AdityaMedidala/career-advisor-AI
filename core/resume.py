import pdfplumber
from typing import Optional, BinaryIO

def extract_text_from_pdf(file: BinaryIO) -> str:
    text = []
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text.append(p.extract_text() or "")
    return "\n".join(text).strip()

def get_text(uploaded_file: Optional[BinaryIO], fallback_text: str) -> str:
    if uploaded_file is not None:
        try:
            return extract_text_from_pdf(uploaded_file)
        except Exception:
            pass
    return fallback_text or ""
