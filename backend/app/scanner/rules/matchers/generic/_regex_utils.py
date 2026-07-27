import re

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult


def find_regex_matches(parsed: ParsedFile, pattern: re.Pattern[str]) -> list[MatchResult]:
    """Runs `pattern` over the raw source and maps byte offsets to line numbers.

    Regex matchers are the fallback strategy for every language: they are
    the only detection mechanism for languages without a dedicated AST
    parser yet, and are also used for cross-cutting concerns (hardcoded
    secrets, weak crypto identifiers, sensitive logging) that read the same
    regardless of language.
    """
    results: list[MatchResult] = []
    for match in pattern.finditer(parsed.source):
        line_start = parsed.source.count("\n", 0, match.start()) + 1
        line_end = parsed.source.count("\n", 0, match.end()) + 1
        results.append(
            MatchResult(
                line_start=line_start,
                line_end=line_end,
                snippet=parsed.snippet(line_start, line_end),
            )
        )
    return results
