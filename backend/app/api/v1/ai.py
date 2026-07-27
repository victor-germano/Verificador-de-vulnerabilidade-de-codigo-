import uuid

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_ai_service,
    get_current_user,
    get_finding_repository,
    get_project_service,
    get_scan_service,
)
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.finding_repository import FindingRepository
from app.schemas.ai import AITextResponse
from app.services.ai_service import AIService
from app.services.project_service import ProjectService
from app.services.scan_service import ScanService

router = APIRouter(prefix="/ai", tags=["ai"])


async def _authorize_finding_access(
    finding_id: uuid.UUID,
    current_user: User,
    finding_repository: FindingRepository,
    scan_service: ScanService,
    project_service: ProjectService,
) -> None:
    finding = await finding_repository.get_by_id(finding_id)
    if finding is None:
        raise NotFoundError("Finding not found.")
    scan = await scan_service.get_scan(finding.scan_id)
    await project_service.get_project(current_user.id, scan.project_id)  # authorization check


@router.post("/findings/{finding_id}/explain", response_model=AITextResponse)
async def explain_finding(
    finding_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    finding_repository: FindingRepository = Depends(get_finding_repository),
    scan_service: ScanService = Depends(get_scan_service),
    project_service: ProjectService = Depends(get_project_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AITextResponse:
    await _authorize_finding_access(
        finding_id, current_user, finding_repository, scan_service, project_service
    )
    return AITextResponse(text=await ai_service.explain_finding(finding_id))


@router.post("/findings/{finding_id}/suggest-fix", response_model=AITextResponse)
async def suggest_fix(
    finding_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    finding_repository: FindingRepository = Depends(get_finding_repository),
    scan_service: ScanService = Depends(get_scan_service),
    project_service: ProjectService = Depends(get_project_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AITextResponse:
    await _authorize_finding_access(
        finding_id, current_user, finding_repository, scan_service, project_service
    )
    return AITextResponse(text=await ai_service.suggest_fix(finding_id))


@router.post("/scans/{scan_id}/summarize", response_model=AITextResponse)
async def summarize_scan(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
    project_service: ProjectService = Depends(get_project_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AITextResponse:
    scan = await scan_service.get_scan(scan_id)
    await project_service.get_project(current_user.id, scan.project_id)  # authorization check
    return AITextResponse(text=await ai_service.summarize_scan(scan_id))
