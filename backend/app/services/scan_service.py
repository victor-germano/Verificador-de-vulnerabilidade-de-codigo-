import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.core.exceptions import NotFoundError
from app.models.enums import ScanStatus, ScanTargetType
from app.models.finding import Finding
from app.models.scan import Scan
from app.repositories.finding_repository import FindingRepository
from app.repositories.scan_repository import ScanRepository
from app.scanner.engines.analyzer import DetectedFinding
from app.scanner.engines.scanner import ScannerEngine


class ScanService:
    """Orchestrates one scan run: creates the `Scan` record, delegates the
    actual analysis to `ScannerEngine`, persists resulting findings, and
    updates the scan with its final status/score. This is the only place
    where the scanner engine (pure, framework-agnostic) meets persistence.
    """

    def __init__(
        self,
        scan_repository: ScanRepository,
        finding_repository: FindingRepository,
        scanner_engine: ScannerEngine | None = None,
    ) -> None:
        self._scan_repository = scan_repository
        self._finding_repository = finding_repository
        self._scanner_engine = scanner_engine or ScannerEngine()

    async def run_scan(
        self,
        project_id: uuid.UUID,
        target_type: ScanTargetType,
        target_reference: str,
        scan_root: Path,
    ) -> Scan:
        scan = Scan(
            project_id=project_id,
            target_type=target_type,
            target_reference=target_reference,
            status=ScanStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        scan = await self._scan_repository.create(scan)

        start = time.perf_counter()
        try:
            result = self._scanner_engine.scan_path(scan_root)
        except Exception as exc:  # noqa: BLE001 - surfaced on the Scan record, not swallowed
            scan.status = ScanStatus.FAILED
            scan.error_message = str(exc)
            scan.finished_at = datetime.now(UTC)
            return await self._scan_repository.update(scan)

        duration_ms = int((time.perf_counter() - start) * 1000)

        findings = [self._to_orm_finding(scan.id, detected) for detected in result.findings]
        await self._finding_repository.bulk_create(findings)

        scan.status = ScanStatus.COMPLETED
        scan.files_scanned = result.files_scanned
        scan.security_score = result.security_score
        scan.duration_ms = duration_ms
        scan.finished_at = datetime.now(UTC)
        return await self._scan_repository.update(scan)

    async def get_scan(self, scan_id: uuid.UUID) -> Scan:
        scan = await self._scan_repository.get_by_id(scan_id)
        if scan is None:
            raise NotFoundError("Scan not found.")
        return scan

    async def list_by_project(self, project_id: uuid.UUID) -> list[Scan]:
        return await self._scan_repository.list_by_project(project_id)

    @staticmethod
    def _to_orm_finding(scan_id: uuid.UUID, detected: DetectedFinding) -> Finding:
        return Finding(
            scan_id=scan_id,
            rule_id=detected.rule_id,
            rule_name=detected.rule_name,
            category=detected.category,
            severity=detected.severity,
            confidence=detected.confidence,
            language=detected.language,
            owasp=detected.owasp,
            cwe=detected.cwe,
            cvss=detected.cvss,
            file_path=detected.file_path,
            line_start=detected.line_start,
            line_end=detected.line_end,
            code_snippet=detected.code_snippet,
            description=detected.description,
            explanation=detected.explanation,
            impact=detected.impact,
            recommendation=detected.recommendation,
            secure_example=detected.secure_example,
            references="\n".join(detected.references),
        )
