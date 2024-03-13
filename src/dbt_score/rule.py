"""Rule definitions."""


import functools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Type

from dbt_score.models import Model

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


class Rule:
    """The rule base class."""

    description: str
    severity: Severity = Severity.MEDIUM

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore
        """Initializes the subclass."""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "description"):
            raise TypeError("Subclass must define class attribute `description`.")

    @classmethod
    def evaluate(cls, model: Model) -> RuleViolation | None:
        """Evaluates the rule."""
        raise NotImplementedError("Subclass must implement class method `evaluate`.")


def rule(
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
) -> Callable[[Callable[[Model], RuleViolation | None]], Type[Rule]]:
    """Rule decorator.

    The rule decorator creates a rule class (subclass of Rule) and returns it.

    Args:
        description: The description of the rule.
        severity: The severity of the rule.
    """

    def decorator_rule(
        func: Callable[[Model], RuleViolation | None],
    ) -> Type[Rule]:
        @functools.wraps(func)
        def wrapper_rule(*args: Any, **kwargs: Any) -> Any:
            logger.debug("Executing `%s` with severity: %s.", func.__name__, severity)
            return func(*args, **kwargs)

        # Create the rule class
        if func.__doc__ is None and description is None:
            raise TypeError("Rule must define `description` or `func.__doc__`.")

        rule_description = description or (
            func.__doc__.split("\n")[0] if func.__doc__ else None
        )
        rule_class = type(
            func.__name__,
            (Rule,),
            {
                "description": rule_description,
                "severity": severity,
                "evaluate": wrapper_rule,
            },
        )

        return rule_class

    return decorator_rule
