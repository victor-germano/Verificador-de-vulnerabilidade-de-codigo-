"""Standalone CLI for the scanner engine.

Deliberately imports only from `app.scanner` (framework-agnostic) - no
FastAPI, no database, no network required. Usable as `sast-cli` (installed
console script) or `python -m app.cli`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.scanner.engines.scanner import ScannerEngine
from app.scanner.reports import ReportContext, ReportExporter, ReportFormat

_SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sast-cli",
        description="Analisa um arquivo ou diretório em busca de vulnerabilidades de segurança.",
    )
    parser.add_argument("path", type=Path, help="Arquivo ou diretório a analisar")
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "html", "pdf"],
        default="json",
        help="Formato do relatório (default: json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Arquivo de saída (obrigatório para --format pdf; default: stdout para os demais)",
    )
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low", "info"],
        default=None,
        help="Encerra com código 1 se houver achado com severidade >= a este nível",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Nome exibido no relatório (default: nome do arquivo/diretório analisado)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    target = args.path.resolve()
    if not target.exists():
        print(f"error: path not found: {target}", file=sys.stderr)
        return 2

    fmt = ReportFormat(args.format)
    if fmt == ReportFormat.PDF and args.output is None:
        print("error: --output is required when --format is pdf", file=sys.stderr)
        return 2

    result = ScannerEngine().scan_path(target)

    context = ReportContext(
        project_name=args.project_name or target.name,
        scan_id="cli-scan",
        generated_at=datetime.now(UTC),
        files_scanned=result.files_scanned,
        security_score=result.security_score,
        findings=result.findings,
    )
    content = ReportExporter().export(fmt, context)

    if args.output:
        args.output.write_bytes(content)
        print(f"Relatório salvo em {args.output}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(content)

    print(
        f"\nArquivos analisados: {result.files_scanned} | "
        f"Vulnerabilidades: {len(result.findings)} | "
        f"Security Score: {result.security_score}/100",
        file=sys.stderr,
    )

    if args.fail_on is not None:
        threshold = _SEVERITY_RANK[args.fail_on]
        if any(_SEVERITY_RANK[f.severity.value] >= threshold for f in result.findings):
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
