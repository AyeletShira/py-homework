from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import os
import hashlib

# אם צריך נתיב מותאם של Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ensure_outdir(outdir_path):
    """
    Creates the output directory if it doesn't exist.
    """
    if not os.path.exists(outdir_path):
        os.makedirs(outdir_path, exist_ok=True)
        print(f"[INFO] Created output directory: {outdir_path}")


def sha256_of_file(filepath):
    """
    Calculates the SHA256 hash of a file — used to verify file uniqueness.
    """
    try:
        with open(filepath, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"[ERROR] Failed to hash file {filepath}: {e}")
        return None


def extract_first_page_text_loosely(pdf_path):
    """
    Extracts text from the first page of a PDF using OCR (Hebrew + English).
    Applies preprocessing for better recognition of RTL text and tables.
    """
    try:
        # Convert first page of PDF to image
        images = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=300)
        if not images:
            print("[WARN] No images found in PDF.")
            return ""

        img = images[0].convert("L")  # Convert to grayscale
        img = ImageOps.autocontrast(img)  # Improve contrast
        img = img.filter(ImageFilter.MedianFilter(3))  # Reduce noise
        img = img.filter(ImageFilter.SHARPEN)  # Sharpen details
        img = img.point(lambda x: 0 if x < 140 else 255, '1')  # Apply threshold

        # OCR configuration
        custom_config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"
        text = pytesseract.image_to_string(img, lang="heb+eng", config=custom_config)

        # Clean up text
        text = text.replace("\r", "").replace("\n\n", "\n").strip()

        # Debug output
        print("[DEBUG OCR OUTPUT (first 400 chars)]:")
        print(text[:400])
        return text

    except Exception as e:
        print("[ERROR in OCR]:", e)
        return ""


import re
from datetime import datetime

def extract_rows_naively_from_pdf(pdf_path, report_type=None):
    """
    Improved extraction: parses day names, dates (dd/mm/yyyy or dd/mm/yy),
    start/end times, and locations. Produces structured rows for the transformer.
    """
    raw_text = extract_first_page_text_loosely(pdf_path)
    if not raw_text:
        return [], {}

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    print(f"[INFO] Extracted {len(lines)} text lines from OCR output.")

    rows = []
    for line in lines:
        # Identify date formats (e.g., 07/10/2022 or 7/9/22)
        date_match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", line)
        time_match = re.findall(r"(\d{1,2}:\d{2})", line)
        location_match = re.search(r"(גלילון|נהריה|ירושלים|חיפה|אשדוד|תל.?אביב|עכו|אשקלון)", line)
        day_match = re.search(r"(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)", line)

        # Parse matches
        date_str = None
        if date_match:
            raw_date = date_match.group(1)
            try:
                # Normalize to yyyy-mm-dd
                parsed_date = datetime.strptime(raw_date, "%d/%m/%Y")
            except ValueError:
                parsed_date = datetime.strptime(raw_date, "%d/%m/%y")
            date_str = parsed_date.strftime("%Y-%m-%d")

        day_name = day_match.group(1) if day_match else None
        start = time_match[0] if len(time_match) > 0 else "08:00"
        end = time_match[1] if len(time_match) > 1 else "16:00"
        location = location_match.group(1) if location_match else None

        # Defaults
        break_min = 30
        total_min = 480

        row = {
            "day": date_str,
            "day_name": day_name,
            "start": start,
            "end": end,
            "break_min": break_min,
            "total_min": total_min,
            "percent_100": 0.0,
            "percent_125": 0.0,
            "percent_150": 0.0,
            "shabbat": 0.0,
            "location": location,
            "_meta": {
                "month": parsed_date.strftime("%Y-%m") if date_str else "unknown"
            }
        }

        rows.append(row)

    meta = {
        "template_version": report_type or "unknown",
        "source_file": str(pdf_path)
    }

    return rows, meta
