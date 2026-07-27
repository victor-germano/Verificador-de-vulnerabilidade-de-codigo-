from datetime import date, datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_projects: int
    total_scans: int
    last_scan_at: datetime | None
    average_security_score: float | None
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int


class SeverityTrendPoint(BaseModel):
    date: date
    critical: int
    high: int
    medium: int
    low: int
    info: int


class TopItem(BaseModel):
    label: str
    count: int
