from __future__ import annotations
from pathlib import Path
from typing import Any, Tuple, List, Dict
import random
from .models import Row, Meta
from .utils import extract_rows_naively_from_pdf


def parse_report_to_rows(pdf_path: Path, report_type: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convert input PDF to a canonical list of row dicts.
    """
    rows, meta = extract_rows_naively_from_pdf(pdf_path, report_type)
    return rows, meta


def vary_rows_deterministically(rows: List[Dict[str, Any]], base_seed: int) -> Dict[str, Any]:
    """
    Apply deterministic but realistic variations to work hours while keeping all fields.
    """
    rnd = random.Random(base_seed)

    varied_rows: List[Dict[str, Any]] = []
    for r in rows:
        try:
            start_h, start_m = map(int, r["start"].split(":"))
            end_h, end_m = map(int, r["end"].split(":"))
        except Exception:
            # fallback if parsing fails
            start_h, start_m, end_h, end_m = 8, 0, 16, 0

        start_total = start_h * 60 + start_m
        end_total = end_h * 60 + end_m

        # jitter start by [-10, +10] minutes
        start_shift = rnd.randint(-10, 10)
        # jitter end by [-10, +20] minutes (bias to longer)
        end_shift = rnd.randint(-10, 20)

        new_start = max(6 * 60, min(21 * 60, start_total + start_shift))
        new_end = max(new_start + 3 * 60, min(23 * 60, end_total + end_shift))

        # break randomization
        shift_len = new_end - new_start
        max_break = max(0, min(45, int(shift_len * 0.2)))
        brk = min(r.get("break_min", 0), max_break)
        brk = max(0, min(max_break, brk + rnd.randint(-10, 10)))

        total_work = shift_len - brk

        # ✅ שימור כל השדות המקוריים
        varied_rows.append({
            **r,
            "start": f"{new_start // 60:02d}:{new_start % 60:02d}",
            "end": f"{new_end // 60:02d}:{new_end % 60:02d}",
            "break_min": brk,
            "total_min": total_work
        })

    month_total_min = sum(r["total_min"] for r in varied_rows)
    print(f"[DEBUG] Created {len(varied_rows)} varied rows (total minutes={month_total_min})")

    return {
        "meta": rows[0].get("_meta", {}),
        "rows": varied_rows,
        "totals": {
            "month_total_min": month_total_min,
            "month_total_hours": round(month_total_min / 60.0, 2)
        }
    }
