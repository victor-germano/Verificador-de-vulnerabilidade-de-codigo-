import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import ProjectRole
from app.models.project_collaborator import ProjectCollaborator


class ProjectCollaboratorRepository(Protocol):
    async def add(self, collaborator: ProjectCollaborator) -> ProjectCollaborator: ...
    async def get(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectCollaborator | None: ...
    async def list_by_project(self, project_id: uuid.UUID) -> list[ProjectCollaborator]: ...
    async def update_role(
        self, collaborator: ProjectCollaborator, role: ProjectRole
    ) -> ProjectCollaborator: ...
    async def remove(self, collaborator: ProjectCollaborator) -> None: ...


class SQLAlchemyProjectCollaboratorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, collaborator: ProjectCollaborator) -> ProjectCollaborator:
        self._session.add(collaborator)
        await self._session.commit()
        await self._session.refresh(collaborator)
        return collaborator

    async def get(self, project_id: uuid.UUID, user_id: uuid.UUID) -> ProjectCollaborator | None:
        result = await self._session.execute(
            select(ProjectCollaborator)
            .where(
                ProjectCollaborator.project_id == project_id,
                ProjectCollaborator.user_id == user_id,
            )
            .options(selectinload(ProjectCollaborator.user))
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> list[ProjectCollaborator]:
        result = await self._session.execute(
            select(ProjectCollaborator)
            .where(ProjectCollaborator.project_id == project_id)
            .options(selectinload(ProjectCollaborator.user))
            .order_by(ProjectCollaborator.created_at.asc())
        )
        return list(result.scalars().all())

    async def update_role(
        self, collaborator: ProjectCollaborator, role: ProjectRole
    ) -> ProjectCollaborator:
        collaborator.role = role
        await self._session.commit()
        # Only refresh the column that changed - a full refresh() would
        # also expire (and require re-loading) the `.user` relationship,
        # which the caller already has selectin-loaded.
        await self._session.refresh(collaborator, attribute_names=["role"])
        return collaborator

    async def remove(self, collaborator: ProjectCollaborator) -> None:
        await self._session.delete(collaborator)
        await self._session.commit()
