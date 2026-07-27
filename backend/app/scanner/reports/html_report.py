from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.scanner.reports.context import ReportContext

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "jinja2"]),
)


class HtmlReportGenerator:
    def generate(self, context: ReportContext) -> str:
        template = _env.get_template("report.html.jinja2")
        return template.render(context=context)
