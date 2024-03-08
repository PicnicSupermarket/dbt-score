import functools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from dbt_score.manifest import Model

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Severity(Enum):
    """The severity/weight of a rule."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RuleViolation:
    """The violation of a rule."""

    message: str | None = None


def rule(
    description: str,
    hint: str,
    severity: Severity = Severity.MEDIUM,
) -> Callable[[Callable[[Model], RuleViolation | None]], Callable[..., None]]:
    """Rule decorator."""

    def decorator_rule(
        func: Callable[[Model], RuleViolation | None],
    ) -> Callable[..., None]:
        @functools.wraps(func)
        def wrapper_rule(*args: Any, **kwargs: Any) -> Any:
            logger.debug("Executing `%s` with severity: %s.", func.__name__, severity)
            return func(*args, **kwargs)

        return wrapper_rule

    return decorator_rule
