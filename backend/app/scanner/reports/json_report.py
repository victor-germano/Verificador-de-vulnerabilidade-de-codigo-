import json
from dataclasses import asdict

from app.scanner.reports.context import ReportContext


class JsonReportGenerator:
    def generate(self, context: ReportContext) -> str:
        payload = {
            "project_name": context.project_name,
            "scan_id": context.scan_id,
            "generated_at": context.generated_at.isoformat(),
            "files_scanned": context.files_scanned,
            "security_score": context.security_score,
            "severity_counts": context.severity_counts,
            "findings": [self._finding_dict(f) for f in context.findings],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @staticmethod
    def _finding_dict(finding) -> dict:
        data = asdict(finding)
        data["severity"] = finding.severity.value
        data["confidence"] = finding.confidence.value
        data["language"] = finding.language.value
        return data
