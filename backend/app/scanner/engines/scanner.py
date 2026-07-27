from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from app.scanner.engines.analyzer import Analyzer, DetectedFinding
from app.scanner.engines.detector import Detector
from app.scanner.engines.risk_calculator import RiskCalculator
from app.scanner.engines.rule_engine import RuleEngine
from app.scanner.parsers.registry import ParserRegistry

_IGNORED_DIR_NAMES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


@dataclass
class ScanResult:
    findings: list[DetectedFinding] = field(default_factory=list)
    files_scanned: int = 0
    security_score: int = 100


class ScannerEngine:
    """Top-level orchestrator: walks the target path, dispatches each file
    to its language parser, runs the rule engine against it via `Detector`,
    and aggregates the result through `Analyzer` + `RiskCalculator`.

    This is the only class `ScanService` (application layer) talks to -
    everything else in `scanner/` is an implementation detail behind it.
    """

    def __init__(
        self,
        parser_registry: ParserRegistry | None = None,
        rule_engine: RuleEngine | None = None,
        detector: Detector | None = None,
        analyzer: Analyzer | None = None,
        risk_calculator: RiskCalculator | None = None,
    ) -> None:
        self._parser_registry = parser_registry or ParserRegistry()
        self._rule_engine = rule_engine or RuleEngine()
        self._detector = detector or Detector(self._rule_engine)
        self._analyzer = analyzer or Analyzer()
        self._risk_calculator = risk_calculator or RiskCalculator()

    def scan_path(self, root: Path) -> ScanResult:
        findings: list[DetectedFinding] = []
        files_scanned = 0

        for file_path in self._iter_target_files(root):
            parser = self._parser_registry.get_parser_for(file_path)
            if parser is None:
                continue
            try:
                source = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            parsed = parser.parse(file_path, source)
            files_scanned += 1

            detections = self._detector.detect(parsed)
            findings.extend(self._analyzer.build_findings(detections, parsed))

        score = self._risk_calculator.calculate(findings, files_scanned)
        return ScanResult(findings=findings, files_scanned=files_scanned, security_score=score)

    def _iter_target_files(self, root: Path) -> Iterator[Path]:
        if root.is_file():
            yield root
            return
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _IGNORED_DIR_NAMES for part in path.parts):
                continue
            if path.suffix in self._parser_registry.supported_extensions:
                yield path
