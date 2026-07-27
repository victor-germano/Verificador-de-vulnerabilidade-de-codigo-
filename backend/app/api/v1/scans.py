import uuid

from fastapi import APIRouter, Depends, UploadFile, status

from app.api.deps import get_current_user, get_project_service, get_scan_service
from app.models.enums import ScanTargetType
from app.models.user import User
from app.schemas.scan import GitScanRequest, ScanResponse
from app.services.project_service import ProjectService
from app.services.scan_service import ScanService
from app.utils.file_handling import extract_if_archive, new_upload_workspace, save_upload
from app.utils.git_handling import clone_repository

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/upload", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_scan(
    project_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    scan_service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    await project_service.require_editor(current_user.id, project_id)  # authorization check

    workspace = new_upload_workspace()
    saved_path = await save_upload(file, workspace)
    scan_root = extract_if_archive(saved_path)

    target_type = ScanTargetType.FOLDER if scan_root.is_dir() else ScanTargetType.FILE
    scan = await scan_service.run_scan(
        project_id=project_id,
        target_type=target_type,
        target_reference=file.filename or str(saved_path),
        scan_root=scan_root,
    )
    return ScanResponse.model_validate(scan)


@router.post("/git", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_git_repository(
    payload: GitScanRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    scan_service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    await project_service.require_editor(current_user.id, payload.project_id)  # authz check

    workspace = new_upload_workspace()
    scan_root = clone_repository(payload.repository_url, workspace, payload.access_token)

    scan = await scan_service.run_scan(
        project_id=payload.project_id,
        target_type=ScanTargetType.GIT_REPOSITORY,
        target_reference=payload.repository_url,
        scan_root=scan_root,
    )
    return ScanResponse.model_validate(scan)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    scan_service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    scan = await scan_service.get_scan(scan_id)
    await project_service.get_project(current_user.id, scan.project_id)  # authorization check
    return ScanResponse.model_validate(scan)


@router.get("/project/{project_id}", response_model=list[ScanResponse])
async def list_project_scans(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    scan_service: ScanService = Depends(get_scan_service),
) -> list[ScanResponse]:
    await project_service.get_project(current_user.id, project_id)  # authorization check
    scans = await scan_service.list_by_project(project_id)
    return [ScanResponse.model_validate(s) for s in scans]
