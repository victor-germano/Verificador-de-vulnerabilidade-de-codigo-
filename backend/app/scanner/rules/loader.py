from functools import lru_cache
from pathlib import Path

import yaml

from app.scanner.rules.schema import Rule

DEFINITIONS_DIR = Path(__file__).parent / "definitions"


def load_rules(definitions_dir: Path = DEFINITIONS_DIR) -> list[Rule]:
    rules: list[Rule] = []
    for yaml_file in sorted(definitions_dir.glob("*.yaml")):
        raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        rules.append(Rule.model_validate(raw))
    return rules


@lru_cache
def get_rules() -> tuple[Rule, ...]:
    return tuple(load_rules())
