# =============================================================================
#  utils.py  —  Text processing utilities
# =============================================================================

import re
from typing import List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


def extract_text_from_pdf_path(path: str) -> str:
    import pdfplumber
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


def remove_pii(text: str) -> str:
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'(\+?\d[\d\s\-().]{7,}\d)', '[PHONE]', text)
    text = re.sub(r'(https?://)?(www\.)?linkedin\.com/in/[^\s]+', '[LINKEDIN]', text)
    text = re.sub(r'(https?://)?(www\.)?github\.com/[^\s]+', '[GITHUB]', text)
    return text


def split_sentences(text: str) -> List[str]:
    parts = re.split(r'(?<=[.!?])\s+|\n', text)
    return [s.strip() for s in parts if len(s.strip()) > 25]


def extract_experience_years(text: str) -> int:
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    for p in patterns:
        m = re.search(p, text.lower())
        if m:
            return int(m.group(1))
    return 0