🧾 PDF Timesheet Extractor
Overview:
This project automatically extracts structured work-time data from PDF timesheets, such as employee attendance or hourly reports.
It identifies key fields like date, check-in/out hours, break time, work hours at 100%, 125%, 150%, Shabbat, and location — even when the layout varies slightly between files.
The system supports multiple PDF templates and outputs normalized data to JSON and a summarized visual PDF report.

🚀 Features:
📄 Automatic PDF text extraction using OCR (supports Hebrew and English).
🧠 Dynamic structure detection – identifies the correct table layout per document.
🕒 Smart time parsing (start, end, total, breaks, percent columns).
🌍 Hebrew-aware text recognition including reversed text correction.

📊 Output formats:
parsed.json – structured per-day data
varied.json – normalized dataset
varied_report.pdf – generated visual summary

📂 Project Structure
src/
 ├── detectors.py     # Detects the template type of each PDF
 ├── transformers.py  # Cleans and converts raw OCR text into structured data
 ├── models.py        # Defines the data models (Row, Meta, etc.)
 ├── renderers.py     # Generates the final PDF report
 ├── utils.py         # Utility functions (OCR helpers, formatting, etc.)
 └── main.py          # Entry point for running the full pipeline

⚙️ Installation:
Clone or download the project:
git clone <repository-url>
cd project-folder

Install required dependencies:
pip install -r requirements.txt

Make sure Tesseract OCR is installed (for Hebrew support):
Windows:
Download from Tesseract OCR Releases

Linux/Mac:
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-heb

🧭 Usage
To process a PDF file:
python -m src.main --input <input.pdf> --outdir <output-folder>

Example:
python -m src.main --input a_r_9.pdf --outdir out

After running:
out/parsed.json → raw structured data
out/varied.json → normalized version
out/varied_report.pdf → visual formatted output

📊 Example Output (JSON)
{
  "meta": {
    "month": "2022-10",
    "template_version": "A"
  },
  "rows": [
    {
      "day": "2022-10-02",
      "start": "08:00",
      "end": "16:00",
      "break_min": 30,
      "total_min": 480,
      "percent_100": 6.5,
      "percent_125": 0.0,
      "percent_150": 0.0,
      "shabbat": 0.0,
      "location": "גלילון"
    }
  ]
}

🧰 Dependencies:
-pytesseract
-pdf2image
-pandas
-reportlab
-re / json
-argparse

👩‍💻 Author
Developed by Ayelet Surovsky
📧 [ayeletss04@gmail.com]
🕓 Version: 1.0.0
📅 Last updated: November 2025