import uuid

from fastapi import APIRouter, Depends, Response

from app.api.deps import (
    get_current_user,
    get_project_service,
    get_report_service,
    get_scan_service,
)
from app.models.user import User
from app.scanner.reports import ReportFormat
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.services.scan_service import ScanService

router = APIRouter(prefix="/reports", tags=["reports"])

_FILE_EXTENSIONS = {
    ReportFormat.JSON: "json",
    ReportFormat.MARKDOWN: "md",
    ReportFormat.HTML: "html",
    ReportFormat.PDF: "pdf",
}


@router.get("/{scan_id}")
async def export_report(
    scan_id: uuid.UUID,
    format: ReportFormat = ReportFormat.JSON,  # noqa: A002 - matches the query param name
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    scan_service: ScanService = Depends(get_scan_service),
    report_service: ReportService = Depends(get_report_service),
) -> Response:
    scan = await scan_service.get_scan(scan_id)
    project = await project_service.get_project(current_user.id, scan.project_id)

    content, content_type = await report_service.export(scan_id, project.name, format)
    filename = f"report-{scan_id}.{_FILE_EXTENSIONS[format]}"

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
