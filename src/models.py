
from dataclasses import dataclass
from typing import Optional

@dataclass
@dataclass
class Row:
    day: str
    start: str
    end: str
    break_min: int
    total_min: int
    percent_100: float | None = None
    percent_125: float | None = None
    percent_150: float | None = None
    shabbat: float | None = None
    location: str | None = None

@dataclass
class Meta:
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    month: Optional[str] = None     # e.g. "2025-10"
    template_version: Optional[str] = None
