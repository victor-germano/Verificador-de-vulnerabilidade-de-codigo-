import uuid

from app.core.exceptions import ConflictError, NotFoundError
from app.models.enums import ProjectRole
from app.models.project_collaborator import ProjectCollaborator
from app.repositories.project_collaborator_repository import ProjectCollaboratorRepository
from app.repositories.user_repository import UserRepository
from app.services.project_service import ProjectService


class CollaboratorService:
    """Manages who (besides the owner) can access a project. All mutating
    operations require the caller to own the project (`ProjectService.
    require_owner`); viewing the collaborator list only requires read
    access (any role), consistent with how the rest of the project's data
    is gated."""

    def __init__(
        self,
        project_service: ProjectService,
        collaborator_repository: ProjectCollaboratorRepository,
        user_repository: UserRepository,
    ) -> None:
        self._project_service = project_service
        self._collaborator_repository = collaborator_repository
        self._user_repository = user_repository

    async def list_collaborators(
        self, current_user_id: uuid.UUID, project_id: uuid.UUID
    ) -> list[ProjectCollaborator]:
        await self._project_service.get_project(current_user_id, project_id)
        return await self._collaborator_repository.list_by_project(project_id)

    async def add_collaborator(
        self, current_user_id: uuid.UUID, project_id: uuid.UUID, email: str, role: ProjectRole
    ) -> ProjectCollaborator:
        project = await self._project_service.require_owner(current_user_id, project_id)

        user = await self._user_repository.get_by_email(email)
        if user is None:
            raise NotFoundError(f"No user found with email '{email}'.")
        if user.id == project.owner_id:
            raise ConflictError("This user already owns the project.")
        if await self._collaborator_repository.get(project_id, user.id) is not None:
            raise ConflictError("This user is already a collaborator on the project.")

        collaborator = ProjectCollaborator(project_id=project_id, user_id=user.id, role=role)
        collaborator = await self._collaborator_repository.add(collaborator)
        # `add()` only refreshes column attributes - `.user` was never
        # queried for this brand-new row, so set it from what we already
        # fetched above instead of letting the API layer trigger a lazy
        # load (unsupported/fragile on an async session).
        collaborator.user = user
        return collaborator

    async def update_role(
        self,
        current_user_id: uuid.UUID,
        project_id: uuid.UUID,
        collaborator_user_id: uuid.UUID,
        role: ProjectRole,
    ) -> ProjectCollaborator:
        await self._project_service.require_owner(current_user_id, project_id)
        collaborator = await self._get_collaborator_or_404(project_id, collaborator_user_id)
        return await self._collaborator_repository.update_role(collaborator, role)

    async def remove_collaborator(
        self, current_user_id: uuid.UUID, project_id: uuid.UUID, collaborator_user_id: uuid.UUID
    ) -> None:
        await self._project_service.require_owner(current_user_id, project_id)
        collaborator = await self._get_collaborator_or_404(project_id, collaborator_user_id)
        await self._collaborator_repository.remove(collaborator)

    async def _get_collaborator_or_404(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectCollaborator:
        collaborator = await self._collaborator_repository.get(project_id, user_id)
        if collaborator is None:
            raise NotFoundError("This user is not a collaborator on the project.")
        return collaborator
