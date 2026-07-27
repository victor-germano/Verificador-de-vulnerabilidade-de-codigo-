from anthropic import Anthropic

from app.scanner.ai.analyzer import AIAnalyzer
from app.scanner.engines.analyzer import DetectedFinding

_SYSTEM_PROMPT = (
    "Você é um especialista sênior em segurança de aplicações (AppSec) revisando "
    "achados de uma ferramenta de análise estática (SAST). Seja direto, técnico e "
    "responda sempre em português do Brasil."
)


class AnthropicAIAnalyzer(AIAnalyzer):
    """`AIAnalyzer` backed by the Anthropic Messages API.

    Enriches the rule-driven text already on `DetectedFinding`
    (description/explanation/impact/recommendation, all deterministic and
    always present regardless of AI availability) with model-generated
    analysis specific to the *exact* code snippet - it never decides
    whether something is a finding; the rule engine remains the sole
    source of truth for that.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def explain(self, finding: DetectedFinding) -> str:
        prompt = (
            f"Explique por que o trecho de código abaixo é uma vulnerabilidade de "
            f"{finding.rule_name} ({finding.cwe}). Não repita a descrição genérica da "
            f"regra - foque em por que *este* trecho específico é explorável, "
            f"considerando o contexto ao redor.\n\n"
            f"Arquivo: {finding.file_path} (linha {finding.line_start})\n"
            f"```\n{finding.code_snippet}\n```"
        )
        return self._complete(prompt)

    def suggest_fix(self, finding: DetectedFinding) -> str:
        prompt = (
            f"Reescreva o trecho de código abaixo corrigindo a vulnerabilidade de "
            f"{finding.rule_name} ({finding.cwe}), preservando o comportamento "
            f"original o máximo possível. Responda apenas com o código corrigido "
            f"em um bloco de código, sem explicação adicional.\n\n"
            f"```\n{finding.code_snippet}\n```"
        )
        return self._complete(prompt)

    def summarize(self, findings: list[DetectedFinding]) -> str:
        if not findings:
            return "Nenhuma vulnerabilidade encontrada neste scan."

        findings_list = "\n".join(
            f"- [{f.severity.value}] {f.rule_name} ({f.cwe}) em {f.file_path}:{f.line_start}"
            for f in findings
        )
        prompt = (
            "Escreva um resumo executivo (3-5 frases) para um relatório de análise "
            "estática, com base na lista de vulnerabilidades abaixo. Destaque o "
            "estado geral de segurança do código e os riscos mais críticos a "
            "priorizar primeiro.\n\n" + findings_list
        )
        return self._complete(prompt)

    def _complete(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()
