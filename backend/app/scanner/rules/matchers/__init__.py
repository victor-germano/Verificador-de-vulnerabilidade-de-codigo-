"""Importing this package registers every matcher against `matcher_registry`.

`RuleEngine` (see `scanner/engines/rule_engine.py`) imports this module once
at startup precisely so the `@register_matcher(...)` decorators below run.
"""

from app.scanner.rules.matchers.csharp import (  # noqa: F401
    sql_and_command as csharp_sql_and_command,
)
from app.scanner.rules.matchers.generic import secrets_and_logging  # noqa: F401
from app.scanner.rules.matchers.go import sql_and_command as go_sql_and_command  # noqa: F401
from app.scanner.rules.matchers.java import sql_and_command as java_sql_and_command  # noqa: F401
from app.scanner.rules.matchers.javascript import command_injection, dom_and_eval  # noqa: F401
from app.scanner.rules.matchers.php import sql_and_command as php_sql_and_command  # noqa: F401
from app.scanner.rules.matchers.python import (  # noqa: F401
    crypto_and_random,
    deserialization_and_xxe,
    injection,
    misc,
    paths_and_network,
    resource_leak,
    web,
)
from app.scanner.rules.matchers.rust import sql_and_command as rust_sql_and_command  # noqa: F401
