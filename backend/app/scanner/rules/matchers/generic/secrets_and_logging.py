import re

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.generic._regex_utils import find_regex_matches

_PASSWORD_PATTERN = re.compile(
    r"""(?i)\b(password|senha|passwd|pwd)\s*[:=]\s*["']([^"'\s]{4,})["']"""
)
_SECRET_PATTERN = re.compile(
    r"""(?i)\b(api[_-]?key|apikey|access[_-]?key|secret|token|auth[_-]?token)"""
    r"""\s*[:=]\s*["']([A-Za-z0-9_\-.]{8,})["']"""
)
_WEAK_CIPHER_PATTERN = re.compile(
    r"""(?i)(DES\.new|MODE_ECB|Cipher\.getInstance\(\s*["']DES|createCipheriv\(\s*["']des)"""
)
_LOG_SENSITIVE_PATTERN = re.compile(
    r"""(?i)\b(logging\.\w+|logger\.\w+|console\.\w+|print)\s*\([^)]*\b"""
    r"""(password|senha|token|secret)\b"""
)

_PLACEHOLDER_HINTS = ("changeme", "your-", "xxx", "<", "example", "placeholder", "dummy")


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in _PLACEHOLDER_HINTS)


@register_matcher("SECRET001")
def match_hardcoded_password(parsed: ParsedFile) -> list[MatchResult]:
    results: list[MatchResult] = []
    for match in _PASSWORD_PATTERN.finditer(parsed.source):
        if _looks_like_placeholder(match.group(2)):
            continue
        line_start = parsed.source.count("\n", 0, match.start()) + 1
        results.append(
            MatchResult(
                line_start=line_start, line_end=line_start, snippet=parsed.snippet(line_start)
            )
        )
    return results


@register_matcher("SECRET002")
def match_hardcoded_secret(parsed: ParsedFile) -> list[MatchResult]:
    results: list[MatchResult] = []
    for match in _SECRET_PATTERN.finditer(parsed.source):
        if _looks_like_placeholder(match.group(2)):
            continue
        line_start = parsed.source.count("\n", 0, match.start()) + 1
        results.append(
            MatchResult(
                line_start=line_start, line_end=line_start, snippet=parsed.snippet(line_start)
            )
        )
    return results


@register_matcher("CRYPTO002")
def match_weak_cipher(parsed: ParsedFile) -> list[MatchResult]:
    return find_regex_matches(parsed, _WEAK_CIPHER_PATTERN)


@register_matcher("LOG001")
def match_sensitive_logging(parsed: ParsedFile) -> list[MatchResult]:
    return find_regex_matches(parsed, _LOG_SENSITIVE_PATTERN)
