import argparse
from pathlib import Path
import json
import os

from .detectors import detect_report_type
from .transformers import parse_report_to_rows, vary_rows_deterministically
from .renderers import render_report_to_pdf
from .utils import ensure_outdir, sha256_of_file


def run(input_pdf: Path, outdir: Path, seed: int | None, force_type: str | None):
    """
    Main pipeline runner:
    1. Detect report type (A or N)
    2. Parse to rows
    3. Vary deterministically
    4. Render new PDF
    """

    # Detect or force report type
    doc_hash = sha256_of_file(input_pdf)
    report_type = force_type or detect_report_type(input_pdf)
    print(f"[INFO] Detected report type: {report_type}")

    # Create output directory for this type
    subfolder_name = f"{report_type}_reports"
    full_outdir = outdir / subfolder_name
    ensure_outdir(full_outdir)

    # 1) Parse to canonical rows
    print("[STEP 1] Parsing PDF...")
    rows, meta = parse_report_to_rows(input_pdf, report_type)
    parsed_path = full_outdir / "parsed.json"
    parsed_path.write_text(json.dumps({"meta": meta, "rows": rows}, ensure_ascii=False, indent=2))
    print(f"[OK] Parsed data saved to {parsed_path}")

    # 2) Vary deterministically (add some randomized variation)
    print("[STEP 2] Applying deterministic variation...")
    varied = vary_rows_deterministically(rows, base_seed=seed or int(doc_hash[:8], 16))
    varied_path = full_outdir / "varied.json"
    varied_path.write_text(json.dumps(varied, ensure_ascii=False, indent=2))
    print(f"[OK] Varied data saved to {varied_path}")

    # 3) Render to a new PDF using same template layout
    print("[STEP 3] Rendering new PDF...")
    out_pdf_path = full_outdir / "varied_report.pdf"

    try:
        if isinstance(varied, dict) and "rows" in varied:
            rows_for_pdf = varied["rows"]
        else:
            rows_for_pdf = varied

        print(f"[DEBUG] Rendering {len(rows_for_pdf)} rows to {out_pdf_path}")
        render_report_to_pdf(rows_for_pdf, meta, out_pdf_path, report_type=report_type)
        print(f"[DONE] Generated new report: {out_pdf_path}")

    except Exception as e:
        print(f"[ERROR] Failed to render PDF: {e}")

    print(f"\n[INFO] All files created under: {full_outdir}")


def main():
    """Command-line entry point."""
    ap = argparse.ArgumentParser(description="PDF Report Parser & Renderer")
    ap.add_argument("--input", required=True, type=Path, help="Path to input PDF file")
    ap.add_argument("--outdir", default=Path("./out"), type=Path, help="Output directory")
    ap.add_argument("--seed", type=int, default=None, help="Randomization seed (optional)")
    ap.add_argument("--force_type", choices=["A", "N"], default=None, help="Force report type (A or N)")
    args = ap.parse_args()

    run(args.input, args.outdir, args.seed, args.force_type)


if __name__ == "__main__":
    main()
