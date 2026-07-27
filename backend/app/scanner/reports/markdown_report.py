from app.scanner.reports.context import ReportContext

_SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


class MarkdownReportGenerator:
    def generate(self, context: ReportContext) -> str:
        lines: list[str] = [
            f"# Relatório de Segurança - {context.project_name}",
            "",
            f"- **Scan ID:** {context.scan_id}",
            f"- **Gerado em:** {context.generated_at.isoformat()}",
            f"- **Arquivos analisados:** {context.files_scanned}",
            f"- **Security Score:** {context.security_score}/100",
            f"- **Total de vulnerabilidades:** {len(context.findings)}",
            "",
            "## Resumo por severidade",
            "",
        ]
        counts = context.severity_counts
        for severity in _SEVERITY_ORDER:
            lines.append(f"- **{severity.capitalize()}:** {counts.get(severity, 0)}")
        lines.append("")
        lines.append("## Vulnerabilidades encontradas")
        lines.append("")

        for finding in context.findings:
            title = f"{finding.rule_name} ({finding.rule_id})"
            location = f"`{finding.file_path}` (linhas {finding.line_start}-{finding.line_end})"
            lines.extend(
                [
                    f"### [{finding.severity.value.upper()}] {title}",
                    "",
                    f"- **Arquivo:** {location}",
                    f"- **Categoria:** {finding.category}",
                    f"- **OWASP:** {finding.owasp}",
                    f"- **CWE:** {finding.cwe}",
                    f"- **CVSS:** {finding.cvss}",
                    f"- **Confiança:** {finding.confidence.value}",
                    "",
                    "**Trecho de código:**",
                    "```",
                    finding.code_snippet,
                    "```",
                    "",
                    f"**Descrição:** {finding.description}",
                    "",
                    f"**Explicação técnica:** {finding.explanation}",
                    "",
                    f"**Impacto:** {finding.impact}",
                    "",
                    f"**Recomendação:** {finding.recommendation}",
                    "",
                    "**Exemplo seguro:**",
                    "```",
                    finding.secure_example,
                    "```",
                    "",
                ]
            )
            if finding.references:
                lines.append("**Referências:**")
                lines.extend(f"- {ref}" for ref in finding.references)
                lines.append("")

        return "\n".join(lines)
