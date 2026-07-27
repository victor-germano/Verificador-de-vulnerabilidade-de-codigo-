import uuid
from datetime import UTC, datetime

from app.core.exceptions import NotFoundError
from app.repositories.finding_repository import FindingFilter, FindingRepository
from app.repositories.scan_repository import ScanRepository
from app.scanner.reports import ReportContext, ReportExporter, ReportFormat
from app.services.finding_mapping import to_detected_finding


class ReportService:
    def __init__(
        self,
        scan_repository: ScanRepository,
        finding_repository: FindingRepository,
        exporter: ReportExporter | None = None,
    ) -> None:
        self._scan_repository = scan_repository
        self._finding_repository = finding_repository
        self._exporter = exporter or ReportExporter()

    async def export(
        self, scan_id: uuid.UUID, project_name: str, fmt: ReportFormat
    ) -> tuple[bytes, str]:
        scan = await self._scan_repository.get_by_id(scan_id)
        if scan is None:
            raise NotFoundError("Scan not found.")

        findings = await self._finding_repository.search(FindingFilter(scan_id=scan_id))
        context = ReportContext(
            project_name=project_name,
            scan_id=str(scan.id),
            generated_at=datetime.now(UTC),
            files_scanned=scan.files_scanned,
            security_score=scan.security_score or 0,
            findings=[to_detected_finding(f) for f in findings],
        )
        content = self._exporter.export(fmt, context)
        return content, self._exporter.content_type(fmt)
