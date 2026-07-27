from enum import StrEnum

from app.scanner.reports.context import ReportContext
from app.scanner.reports.html_report import HtmlReportGenerator
from app.scanner.reports.json_report import JsonReportGenerator
from app.scanner.reports.markdown_report import MarkdownReportGenerator
from app.scanner.reports.pdf_report import PdfReportGenerator


class ReportFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


_CONTENT_TYPES: dict[ReportFormat, str] = {
    ReportFormat.JSON: "application/json",
    ReportFormat.MARKDOWN: "text/markdown",
    ReportFormat.HTML: "text/html",
    ReportFormat.PDF: "application/pdf",
}


class ReportExporter:
    """Single entry point the API uses to generate a report in any
    supported format. Adding a new format means adding one generator class
    and one branch here - nothing else in the codebase needs to change.
    """

    def __init__(self) -> None:
        self._json = JsonReportGenerator()
        self._markdown = MarkdownReportGenerator()
        self._html = HtmlReportGenerator()
        self._pdf = PdfReportGenerator()

    def content_type(self, fmt: ReportFormat) -> str:
        return _CONTENT_TYPES[fmt]

    def export(self, fmt: ReportFormat, context: ReportContext) -> bytes:
        if fmt == ReportFormat.JSON:
            return self._json.generate(context).encode("utf-8")
        if fmt == ReportFormat.MARKDOWN:
            return self._markdown.generate(context).encode("utf-8")
        if fmt == ReportFormat.HTML:
            return self._html.generate(context).encode("utf-8")
        if fmt == ReportFormat.PDF:
            return self._pdf.generate(context)
        raise ValueError(f"Unsupported report format: {fmt}")
