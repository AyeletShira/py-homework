from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import io

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
        img = img.filter(ImageFilter.SHARPEN)  # Sharpen details
        img = img.point(lambda x: 0 if x < 140 else 255, '1')  # Apply threshold

        # OCR configuration
        custom_config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"
        text = pytesseract.image_to_string(img, lang="heb+eng", config=custom_config)

        # Debug print to verify OCR output
        print("[DEBUG OCR OUTPUT (first 400 chars)]:", text[:400])
        return text

    except Exception as e:
        print("[ERROR in OCR]:", e)
        return ""
