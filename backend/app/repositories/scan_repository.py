import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scan import Scan


class ScanRepository(Protocol):
    async def get_by_id(self, scan_id: uuid.UUID) -> Scan | None: ...
    async def list_by_project(self, project_id: uuid.UUID) -> list[Scan]: ...
    async def list_recent(self, owner_id: uuid.UUID, limit: int) -> list[Scan]: ...
    async def create(self, scan: Scan) -> Scan: ...
    async def update(self, scan: Scan) -> Scan: ...


class SQLAlchemyScanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, scan_id: uuid.UUID) -> Scan | None:
        result = await self._session.execute(
            select(Scan).where(Scan.id == scan_id).options(selectinload(Scan.findings))
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> list[Scan]:
        result = await self._session.execute(
            select(Scan).where(Scan.project_id == project_id).order_by(Scan.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_recent(self, owner_id: uuid.UUID, limit: int = 10) -> list[Scan]:
        from app.models.project import Project

        result = await self._session.execute(
            select(Scan)
            .join(Project, Scan.project_id == Project.id)
            .where(Project.owner_id == owner_id)
            .order_by(Scan.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, scan: Scan) -> Scan:
        self._session.add(scan)
        await self._session.commit()
        await self._session.refresh(scan)
        return scan

    async def update(self, scan: Scan) -> Scan:
        await self._session.commit()
        await self._session.refresh(scan)
        return scan
