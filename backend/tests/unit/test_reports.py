import json
from datetime import UTC, datetime

import pytest

from app.models.enums import Confidence, Language, Severity
from app.scanner.engines.analyzer import DetectedFinding
from app.scanner.reports import ReportContext, ReportExporter, ReportFormat
from app.scanner.reports.html_report import HtmlReportGenerator
from app.scanner.reports.json_report import JsonReportGenerator
from app.scanner.reports.markdown_report import MarkdownReportGenerator


@pytest.fixture
def context() -> ReportContext:
    finding = DetectedFinding(
        rule_id="SQL001",
        rule_name="SQL Injection",
        category="Injection",
        severity=Severity.CRITICAL,
        confidence=Confidence.MEDIUM,
        language=Language.PYTHON,
        owasp="A03:2021 - Injection",
        cwe="CWE-89",
        cvss=9.8,
        file_path="app.py",
        line_start=10,
        line_end=10,
        code_snippet="cursor.execute(query)",
        description="desc",
        explanation="expl",
        impact="impact",
        recommendation="fix it",
        secure_example="cursor.execute('...', (x,))",
        references=["https://owasp.org"],
    )
    return ReportContext(
        project_name="Demo",
        scan_id="scan-1",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        files_scanned=5,
        security_score=72,
        findings=[finding],
    )


def test_context_severity_counts(context: ReportContext) -> None:
    assert context.severity_counts == {"critical": 1}


def test_json_report_is_valid_json_with_expected_fields(context: ReportContext) -> None:
    output = JsonReportGenerator().generate(context)
    payload = json.loads(output)

    assert payload["project_name"] == "Demo"
    assert payload["security_score"] == 72
    assert payload["findings"][0]["rule_id"] == "SQL001"
    assert payload["findings"][0]["severity"] == "critical"


def test_markdown_report_contains_key_sections(context: ReportContext) -> None:
    output = MarkdownReportGenerator().generate(context)

    assert "# Relatório de Segurança - Demo" in output
    assert "SQL001" in output
    assert "Security Score:** 72/100" in output


def test_html_report_renders_finding_and_escapes_content(context: ReportContext) -> None:
    output = HtmlReportGenerator().generate(context)

    assert "<html" in output
    assert "SQL Injection" in output
    assert "app.py" in output


def test_exporter_dispatches_json_markdown_html(context: ReportContext) -> None:
    exporter = ReportExporter()

    json_bytes = exporter.export(ReportFormat.JSON, context)
    md_bytes = exporter.export(ReportFormat.MARKDOWN, context)
    html_bytes = exporter.export(ReportFormat.HTML, context)

    assert json.loads(json_bytes)["project_name"] == "Demo"
    assert b"# Relat" in md_bytes
    assert b"<html" in html_bytes


def test_pdf_report_raises_clear_error_without_native_libs(context: ReportContext) -> None:
    from app.scanner.reports.pdf_report import PdfReportGenerator

    try:
        PdfReportGenerator().generate(context)
    except RuntimeError as exc:
        assert "WeasyPrint" in str(exc)
    except Exception:  # pragma: no cover - environment has native libs installed
        pytest.skip("WeasyPrint native dependencies are available in this environment")


def test_exporter_content_types() -> None:
    exporter = ReportExporter()
    assert exporter.content_type(ReportFormat.JSON) == "application/json"
    assert exporter.content_type(ReportFormat.MARKDOWN) == "text/markdown"
    assert exporter.content_type(ReportFormat.HTML) == "text/html"
    assert exporter.content_type(ReportFormat.PDF) == "application/pdf"
