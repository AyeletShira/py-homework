from pathlib import Path
from .utils import extract_first_page_text_loosely


def detect_report_type(pdf_path: Path) -> str:
    """
    Detects the report type (A or N) based on filename or light text scan.
    Uses OCR fallback through extract_first_page_text_loosely if needed.
    """

    name = pdf_path.name.lower()
    text = extract_first_page_text_loosely(pdf_path).lower()

    # 1. Filename-based detection (most reliable)
    if "a_r_" in name:
        return "A"
    if "n_r_" in name:
        return "N"

    # 2. Text-based fallback (for unexpected file names)
    if any(word in text for word in ["total", "hours", "שעות", "כניסה", "יציאה"]):
        return "A"
    if any(word in text for word in ["daily", "sum", "report", "דו״ח", "דוח"]):
        return "N"

    # 3. Default to A (safe fallback)
    return "A"
