from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


# -------------------------------------------------------------
# Hebrew (Right-To-Left) Support
# -------------------------------------------------------------
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # Font with Hebrew support

def fix_rtl(s: str) -> str:
    """
    Reverse Hebrew text to display correctly (Right-to-Left).
    """
    if not isinstance(s, str):
        return s
    return s[::-1]


# -------------------------------------------------------------
# Main rendering function
# -------------------------------------------------------------
def render_report_to_pdf(rows, meta, out_path: Path, report_type: str = "A"):
    if report_type.upper() == "A":
        return render_report_to_pdf_type_a(rows, meta, out_path)
    else:
        return render_report_to_pdf_type_n(rows, meta, out_path)


# -------------------------------------------------------------
# TYPE A – Full structured report (includes percentages)
# -------------------------------------------------------------
def render_report_to_pdf_type_a(rows, meta, out_path: Path):
    styles = getSampleStyleSheet()
    hebrew_style = ParagraphStyle(
        name='Hebrew',
        fontName='STSong-Light',
        alignment=2,  # Align right
        leading=14
    )

    story = []

    month_label = meta.get("month", "לא ידוע")
    title = fix_rtl(f"דוח שעות לעובד - {month_label}")
    story.append(Paragraph(title, hebrew_style))
    story.append(Spacer(1, 20))

    # Header row for Type A
    header = [[
        fix_rtl("תאריך"),
        fix_rtl("יום"),
        fix_rtl("מקום"),
        fix_rtl("כניסה"),
        fix_rtl("יציאה"),
        fix_rtl("הפסקה"),
        fix_rtl("סה״כ"),
        fix_rtl("100%"),
        fix_rtl("125%"),
        fix_rtl("150%"),
        fix_rtl("שבת")
    ]]

    # Table data
    data = []
    for row in rows:
        total_hours = round(row["total_min"] / 60, 2)
        data.append([
            fix_rtl(row.get("day", "")),
            fix_rtl(row.get("day_name", "") or ""),
            fix_rtl(row.get("location", "") or ""),
            row.get("start", ""),
            row.get("end", ""),
            f"{row.get('break_min', 0)} דק׳",
            total_hours,
            row.get("percent_100", 0.0),
            row.get("percent_125", 0.0),
            row.get("percent_150", 0.0),
            row.get("shabbat", 0.0)
        ])

    table_data = header + data

    # Table style
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Totals summary
    total_hrs = sum(r["total_min"] for r in rows) / 60
    sum100 = sum(r.get("percent_100", 0) for r in rows)
    sum125 = sum(r.get("percent_125", 0) for r in rows)
    sum150 = sum(r.get("percent_150", 0) for r in rows)
    sum_shabbat = sum(r.get("shabbat", 0) for r in rows)

    summary_text = (
        f"<b>{fix_rtl('סה״כ שעות')}:</b> {total_hrs:.1f}<br/>"
        f"<b>{fix_rtl('שעות 100%')}:</b> {sum100:.1f}&nbsp;&nbsp;"
        f"<b>{fix_rtl('125%')}:</b> {sum125:.1f}&nbsp;&nbsp;"
        f"<b>{fix_rtl('150%')}:</b> {sum150:.1f}&nbsp;&nbsp;"
        f"<b>{fix_rtl('שבת')}:</b> {sum_shabbat:.1f}"
    )

    story.append(Paragraph(summary_text, hebrew_style))

    # Build PDF
    doc = SimpleDocTemplate(str(out_path),
                            pagesize=landscape(A4),
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    doc.build(story)

    print(f"[OK] Hebrew Type A report generated: {out_path}")


# -------------------------------------------------------------
# TYPE N – Simple scanned report (with remarks)
# -------------------------------------------------------------
def render_report_to_pdf_type_n(rows, meta, out_path: Path):
    styles = getSampleStyleSheet()
    hebrew_style = ParagraphStyle(
        name='Hebrew',
        fontName='STSong-Light',
        alignment=2,  # Align right
        leading=14
    )

    story = []

    month_label = meta.get("month", "לא ידוע")
    title = fix_rtl(f"דוח סרוק - {month_label}")
    story.append(Paragraph(title, hebrew_style))
    story.append(Spacer(1, 20))

    # Header row for Type N
    header = [[
        fix_rtl("תאריך"),
        fix_rtl("יום בשבוע"),
        fix_rtl("שעת כניסה"),
        fix_rtl("שעת יציאה"),
        fix_rtl("סה״כ שעות"),
        fix_rtl("הערות")
    ]]

    # Table data
    data = []
    for row in rows:
        total_hours = round(row["total_min"] / 60, 2)
        data.append([
            fix_rtl(row.get("day", "")),
            fix_rtl(row.get("day_name", "") or ""),
            row.get("start", ""),
            row.get("end", ""),
            total_hours,
            fix_rtl(row.get("location", "") or "")  # Remarks column
        ])

    table_data = header + data

    # Table style
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    total_hrs = sum(r["total_min"] for r in rows) / 60
    story.append(Paragraph(f"<b>{fix_rtl('סה״כ שעות')}:</b> {total_hrs:.1f}", hebrew_style))

    # Build PDF
    doc = SimpleDocTemplate(str(out_path),
                            pagesize=landscape(A4),
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    doc.build(story)

    print(f"[OK] Hebrew Type N report generated: {out_path}")
