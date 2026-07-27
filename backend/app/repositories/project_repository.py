import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_collaborator import ProjectCollaborator


class ProjectRepository(Protocol):
    async def get_by_id(self, project_id: uuid.UUID) -> Project | None: ...
    async def list_accessible_to(self, user_id: uuid.UUID) -> list[Project]: ...
    async def create(self, project: Project) -> Project: ...
    async def delete(self, project: Project) -> None: ...


class SQLAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return await self._session.get(Project, project_id)

    async def list_accessible_to(self, user_id: uuid.UUID) -> list[Project]:
        """Projects the user owns, plus projects they're a collaborator on."""
        collaborator_project_ids = select(ProjectCollaborator.project_id).where(
            ProjectCollaborator.user_id == user_id
        )
        result = await self._session.execute(
            select(Project)
            .where((Project.owner_id == user_id) | (Project.id.in_(collaborator_project_ids)))
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, project: Project) -> Project:
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self._session.delete(project)
        await self._session.commit()
