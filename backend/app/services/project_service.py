import uuid
from typing import Literal

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.enums import ProjectRole
from app.models.project import Project
from app.repositories.project_collaborator_repository import ProjectCollaboratorRepository
from app.repositories.project_repository import ProjectRepository

EffectiveRole = Literal["owner"] | ProjectRole


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        collaborator_repository: ProjectCollaboratorRepository,
    ) -> None:
        self._project_repository = project_repository
        self._collaborator_repository = collaborator_repository

    async def create_project(
        self, owner_id: uuid.UUID, name: str, description: str | None
    ) -> Project:
        project = Project(name=name, description=description, owner_id=owner_id)
        return await self._project_repository.create(project)

    async def list_projects(self, user_id: uuid.UUID) -> list[Project]:
        return await self._project_repository.list_accessible_to(user_id)

    async def get_project(self, user_id: uuid.UUID, project_id: uuid.UUID) -> Project:
        """Any role (owner/editor/viewer) grants read access."""
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found.")
        role = await self.get_role(user_id, project)
        if role is None:
            raise AuthorizationError("You do not have access to this project.")
        return project

    async def get_role(self, user_id: uuid.UUID, project: Project) -> EffectiveRole | None:
        if project.owner_id == user_id:
            return "owner"
        collaborator = await self._collaborator_repository.get(project.id, user_id)
        return collaborator.role if collaborator else None

    async def require_editor(self, user_id: uuid.UUID, project_id: uuid.UUID) -> Project:
        """Owner or editor - used to gate actions that change project state
        (running a scan), as opposed to merely viewing it."""
        project = await self.get_project(user_id, project_id)
        role = await self.get_role(user_id, project)
        if role == ProjectRole.VIEWER:
            raise AuthorizationError("Viewers cannot perform this action.")
        return project

    async def require_owner(self, user_id: uuid.UUID, project_id: uuid.UUID) -> Project:
        """Owner only - used to gate destructive/administrative actions
        (deleting the project, managing collaborators)."""
        project = await self.get_project(user_id, project_id)
        if project.owner_id != user_id:
            raise AuthorizationError("Only the project owner can perform this action.")
        return project

    async def delete_project(self, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
        project = await self.require_owner(user_id, project_id)
        await self._project_repository.delete(project)
