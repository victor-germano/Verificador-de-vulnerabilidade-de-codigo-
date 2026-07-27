"""Decoupling point between rule metadata (YAML) and detection logic (code).

A matcher is a plain function `ParsedFile -> list[MatchResult]`. It is
registered against a rule id via `@register_matcher("SQL001")`. The rule
engine never imports a matcher module directly - it looks the function up
by id through `get_matcher`, so adding a new rule never requires touching
the engine itself (see `docs/adding-a-rule.md`).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.models.enums import Confidence
from app.scanner.parsers.base import ParsedFile


@dataclass(frozen=True)
class MatchResult:
    line_start: int
    line_end: int
    snippet: str
    confidence: Confidence | None = None
    note: str | None = None


MatcherFn = Callable[[ParsedFile], list[MatchResult]]

_REGISTRY: dict[str, MatcherFn] = {}


def register_matcher(rule_id: str) -> Callable[[MatcherFn], MatcherFn]:
    def decorator(fn: MatcherFn) -> MatcherFn:
        _REGISTRY[rule_id] = fn
        return fn

    return decorator


def get_matcher(rule_id: str) -> MatcherFn | None:
    return _REGISTRY.get(rule_id)


def registered_rule_ids() -> set[str]:
    return set(_REGISTRY)
