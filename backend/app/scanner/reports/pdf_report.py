from app.scanner.reports.context import ReportContext
from app.scanner.reports.html_report import HtmlReportGenerator


class PdfReportGenerator:
    """Renders the same HTML template used by `HtmlReportGenerator` to PDF
    via WeasyPrint, so both formats always stay visually consistent.

    Requires WeasyPrint's system dependencies (Pango, Cairo, GDK-Pixbuf) to
    be present - see `docker/Dockerfile.backend`. The import is deferred to
    `generate()` (rather than module load time) so the rest of the API can
    start and run without those native libraries installed - only actually
    requesting a PDF report requires them.
    """

    def __init__(self, html_generator: HtmlReportGenerator | None = None) -> None:
        self._html_generator = html_generator or HtmlReportGenerator()

    def generate(self, context: ReportContext) -> bytes:
        try:
            from weasyprint import HTML
        except OSError as exc:
            raise RuntimeError(
                "PDF export requires WeasyPrint's native dependencies "
                "(Pango, Cairo, GDK-Pixbuf). They are installed in the Docker "
                "image; see docker/Dockerfile.backend or WeasyPrint's install docs."
            ) from exc

        html = self._html_generator.generate(context)
        return HTML(string=html).write_pdf()
