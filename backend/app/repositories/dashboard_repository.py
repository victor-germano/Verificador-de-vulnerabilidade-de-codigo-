import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Severity
from app.models.finding import Finding
from app.models.project import Project
from app.models.project_collaborator import ProjectCollaborator
from app.models.scan import Scan


def _accessible_to(user_id: uuid.UUID) -> ColumnElement[bool]:
    """Project.id filter matching every project the user can see: the ones
    they own, plus the ones they're a collaborator on (any role) - used
    everywhere below so dashboard numbers reflect shared projects too, not
    just ones the user personally created."""
    collaborator_project_ids = select(ProjectCollaborator.project_id).where(
        ProjectCollaborator.user_id == user_id
    )
    return (Project.owner_id == user_id) | (Project.id.in_(collaborator_project_ids))


class DashboardRepository:
    """Read-only aggregate queries backing the dashboard - kept separate
    from the transactional repositories (`ScanRepository`,
    `FindingRepository`, ...) since these are pure reporting queries with no
    write side, closer to a CQRS read model than a domain repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_projects(self, user_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count(Project.id)).where(_accessible_to(user_id))
        )
        return result.scalar_one()

    async def count_scans(self, user_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count(Scan.id))
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id))
        )
        return result.scalar_one()

    async def last_scan_at(self, user_id: uuid.UUID) -> datetime | None:
        result = await self._session.execute(
            select(func.max(Scan.finished_at))
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id))
        )
        return result.scalar_one_or_none()

    async def average_security_score(self, user_id: uuid.UUID) -> float | None:
        result = await self._session.execute(
            select(func.avg(Scan.security_score))
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id), Scan.security_score.is_not(None))
        )
        value = result.scalar_one_or_none()
        return round(value, 1) if value is not None else None

    async def severity_counts(self, user_id: uuid.UUID) -> dict[Severity, int]:
        result = await self._session.execute(
            select(Finding.severity, func.count(Finding.id))
            .join(Scan, Finding.scan_id == Scan.id)
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id))
            .group_by(Finding.severity)
        )
        return dict(result.all())

    async def top_rules(self, user_id: uuid.UUID, limit: int = 5) -> list[tuple[str, int]]:
        result = await self._session.execute(
            select(Finding.rule_name, func.count(Finding.id).label("total"))
            .join(Scan, Finding.scan_id == Scan.id)
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id))
            .group_by(Finding.rule_name)
            .order_by(func.count(Finding.id).desc())
            .limit(limit)
        )
        return list(result.all())

    async def top_files(self, user_id: uuid.UUID, limit: int = 5) -> list[tuple[str, int]]:
        result = await self._session.execute(
            select(Finding.file_path, func.count(Finding.id).label("total"))
            .join(Scan, Finding.scan_id == Scan.id)
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id))
            .group_by(Finding.file_path)
            .order_by(func.count(Finding.id).desc())
            .limit(limit)
        )
        return list(result.all())

    async def severity_trend(
        self, user_id: uuid.UUID, days: int = 30
    ) -> dict[date, dict[Severity, int]]:
        since = datetime.now(UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(
                func.date(Finding.created_at).label("day"),
                Finding.severity,
                func.count(Finding.id),
            )
            .join(Scan, Finding.scan_id == Scan.id)
            .join(Project, Scan.project_id == Project.id)
            .where(_accessible_to(user_id), Finding.created_at >= since)
            .group_by("day", Finding.severity)
            .order_by("day")
        )
        trend: dict[date, dict[Severity, int]] = {}
        for day, severity, count in result.all():
            trend.setdefault(day, {})[severity] = count
        return trend
