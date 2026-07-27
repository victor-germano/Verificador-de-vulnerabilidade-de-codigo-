import uuid

from app.models.enums import Severity
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardSummary, SeverityTrendPoint, TopItem


class DashboardService:
    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self._repo = dashboard_repository

    async def get_summary(self, user_id: uuid.UUID) -> DashboardSummary:
        severity_counts = await self._repo.severity_counts(user_id)

        return DashboardSummary(
            total_projects=await self._repo.count_projects(user_id),
            total_scans=await self._repo.count_scans(user_id),
            last_scan_at=await self._repo.last_scan_at(user_id),
            average_security_score=await self._repo.average_security_score(user_id),
            total_findings=sum(severity_counts.values()),
            critical_count=severity_counts.get(Severity.CRITICAL, 0),
            high_count=severity_counts.get(Severity.HIGH, 0),
            medium_count=severity_counts.get(Severity.MEDIUM, 0),
            low_count=severity_counts.get(Severity.LOW, 0),
            info_count=severity_counts.get(Severity.INFO, 0),
        )

    async def get_trend(self, user_id: uuid.UUID, days: int = 30) -> list[SeverityTrendPoint]:
        trend = await self._repo.severity_trend(user_id, days=days)
        return [
            SeverityTrendPoint(
                date=day,
                critical=counts.get(Severity.CRITICAL, 0),
                high=counts.get(Severity.HIGH, 0),
                medium=counts.get(Severity.MEDIUM, 0),
                low=counts.get(Severity.LOW, 0),
                info=counts.get(Severity.INFO, 0),
            )
            for day, counts in sorted(trend.items())
        ]

    async def get_top_vulnerabilities(self, user_id: uuid.UUID, limit: int = 5) -> list[TopItem]:
        rows = await self._repo.top_rules(user_id, limit=limit)
        return [TopItem(label=label, count=count) for label, count in rows]

    async def get_top_files(self, user_id: uuid.UUID, limit: int = 5) -> list[TopItem]:
        rows = await self._repo.top_files(user_id, limit=limit)
        return [TopItem(label=label, count=count) for label, count in rows]
