import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_collaborator_service, get_current_user, get_project_service
from app.models.user import User
from app.schemas.collaborator import (
    AddCollaboratorRequest,
    CollaboratorResponse,
    UpdateCollaboratorRoleRequest,
)
from app.schemas.project import ProjectCreateRequest, ProjectResponse
from app.services.collaborator_service import CollaboratorService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    projects = await project_service.list_projects(current_user.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await project_service.create_project(
        current_user.id, payload.name, payload.description
    )
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await project_service.get_project(current_user.id, project_id)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> None:
    await project_service.delete_project(current_user.id, project_id)


@router.get("/{project_id}/collaborators", response_model=list[CollaboratorResponse])
async def list_collaborators(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    collaborator_service: CollaboratorService = Depends(get_collaborator_service),
) -> list[CollaboratorResponse]:
    collaborators = await collaborator_service.list_collaborators(current_user.id, project_id)
    return [
        CollaboratorResponse(
            user_id=c.user_id,
            email=c.user.email,
            full_name=c.user.full_name,
            role=c.role.value,
            added_at=c.created_at,
        )
        for c in collaborators
    ]


@router.post(
    "/{project_id}/collaborators",
    response_model=CollaboratorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_collaborator(
    project_id: uuid.UUID,
    payload: AddCollaboratorRequest,
    current_user: User = Depends(get_current_user),
    collaborator_service: CollaboratorService = Depends(get_collaborator_service),
) -> CollaboratorResponse:
    collaborator = await collaborator_service.add_collaborator(
        current_user.id, project_id, payload.email, payload.role
    )
    return CollaboratorResponse(
        user_id=collaborator.user_id,
        email=collaborator.user.email,
        full_name=collaborator.user.full_name,
        role=collaborator.role.value,
        added_at=collaborator.created_at,
    )


@router.patch(
    "/{project_id}/collaborators/{collaborator_user_id}", response_model=CollaboratorResponse
)
async def update_collaborator_role(
    project_id: uuid.UUID,
    collaborator_user_id: uuid.UUID,
    payload: UpdateCollaboratorRoleRequest,
    current_user: User = Depends(get_current_user),
    collaborator_service: CollaboratorService = Depends(get_collaborator_service),
) -> CollaboratorResponse:
    collaborator = await collaborator_service.update_role(
        current_user.id, project_id, collaborator_user_id, payload.role
    )
    return CollaboratorResponse(
        user_id=collaborator.user_id,
        email=collaborator.user.email,
        full_name=collaborator.user.full_name,
        role=collaborator.role.value,
        added_at=collaborator.created_at,
    )


@router.delete(
    "/{project_id}/collaborators/{collaborator_user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_collaborator(
    project_id: uuid.UUID,
    collaborator_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    collaborator_service: CollaboratorService = Depends(get_collaborator_service),
) -> None:
    await collaborator_service.remove_collaborator(
        current_user.id, project_id, collaborator_user_id
    )
