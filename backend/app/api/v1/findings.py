import uuid
from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_finding_repository, get_project_service
from app.models.enums import Language, Severity
from app.models.user import User
from app.repositories.finding_repository import FindingFilter, FindingRepository
from app.schemas.finding import FindingResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("", response_model=list[FindingResponse])
async def list_findings(
    project_id: uuid.UUID,
    scan_id: uuid.UUID | None = None,
    severity: Severity | None = None,
    language: Language | None = None,
    category: str | None = None,
    file_path: str | None = None,
    created_after: datetime | None = None,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    finding_repository: FindingRepository = Depends(get_finding_repository),
) -> list[FindingResponse]:
    await project_service.get_project(current_user.id, project_id)  # authorization check

    filters = FindingFilter(
        project_id=project_id,
        scan_id=scan_id,
        severity=severity,
        language=language,
        category=category,
        file_path=file_path,
        created_after=created_after,
    )
    findings = await finding_repository.search(filters)
    return [FindingResponse.model_validate(f) for f in findings]
