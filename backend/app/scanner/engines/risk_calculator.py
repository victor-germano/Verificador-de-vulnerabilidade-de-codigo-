from app.models.enums import Severity
from app.scanner.engines.analyzer import DetectedFinding

_SEVERITY_WEIGHT: dict[Severity, float] = {
    Severity.CRITICAL: 15.0,
    Severity.HIGH: 8.0,
    Severity.MEDIUM: 4.0,
    Severity.LOW: 1.5,
    Severity.INFO: 0.5,
}


class RiskCalculator:
    """Computes the 0-100 Security Score shown on the dashboard.

    The score combines two signals:
    - **gravity/quantity**: a weighted sum of findings by severity (a single
      Critical hurts far more than a dozen Info-level ones);
    - **density**: that same penalty normalized by the number of files
      scanned, so a large codebase with a handful of issues isn't penalized
      as harshly as a tiny script with the same absolute count ("coverage"
      proxy - more files scanned clean should not lower the score).

    This is a deliberately simple, documented heuristic meant as a starting
    point; it is isolated in one class specifically so the formula can be
    refined later without touching the rest of the engine.
    """

    def calculate(self, findings: list[DetectedFinding], files_scanned: int) -> int:
        if not findings:
            return 100

        raw_penalty = sum(_SEVERITY_WEIGHT[f.severity] for f in findings)
        density_penalty = raw_penalty / max(files_scanned, 1)
        penalty = min(100.0, raw_penalty * 0.6 + density_penalty * 10)

        return max(0, round(100 - penalty))
