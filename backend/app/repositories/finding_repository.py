import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Language, Severity
from app.models.finding import Finding
from app.models.scan import Scan


@dataclass(frozen=True)
class FindingFilter:
    project_id: uuid.UUID | None = None
    scan_id: uuid.UUID | None = None
    severity: Severity | None = None
    language: Language | None = None
    category: str | None = None
    file_path: str | None = None
    created_after: datetime | None = None


class FindingRepository(Protocol):
    async def bulk_create(self, findings: list[Finding]) -> None: ...
    async def search(self, filters: FindingFilter) -> list[Finding]: ...
    async def get_by_id(self, finding_id: uuid.UUID) -> Finding | None: ...


class SQLAlchemyFindingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def bulk_create(self, findings: list[Finding]) -> None:
        if not findings:
            return
        self._session.add_all(findings)
        await self._session.commit()

    async def get_by_id(self, finding_id: uuid.UUID) -> Finding | None:
        return await self._session.get(Finding, finding_id)

    async def search(self, filters: FindingFilter) -> list[Finding]:
        query = select(Finding)

        if filters.scan_id is not None:
            query = query.where(Finding.scan_id == filters.scan_id)
        if filters.project_id is not None:
            query = query.join(Scan, Finding.scan_id == Scan.id).where(
                Scan.project_id == filters.project_id
            )
        if filters.severity is not None:
            query = query.where(Finding.severity == filters.severity)
        if filters.language is not None:
            query = query.where(Finding.language == filters.language)
        if filters.category is not None:
            query = query.where(Finding.category == filters.category)
        if filters.file_path is not None:
            query = query.where(Finding.file_path.ilike(f"%{filters.file_path}%"))
        if filters.created_after is not None:
            query = query.where(Finding.created_at >= filters.created_after)

        query = query.order_by(Finding.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())
