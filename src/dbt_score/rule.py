"""Rule definitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Type

from dbt_score.models import Model


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

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluates the rule."""
        raise NotImplementedError("Subclass must implement method `evaluate`.")


def rule(
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
) -> Callable[[Callable[[Any, Model], RuleViolation | None]], Type[Rule]]:
    """Rule decorator.

    The rule decorator creates a rule class (subclass of Rule) and returns it.

    Args:
        description: The description of the rule.
        severity: The severity of the rule.
    """

    def decorator_rule(
        func: Callable[[Any, Model], RuleViolation | None],
    ) -> Type[Rule]:
        """Decorator function."""
        if func.__doc__ is None and description is None:
            raise TypeError("Rule must define `description` or `func.__doc__`.")

        # Get description parameter, otherwise use the docstring.
        rule_description = description or (
            func.__doc__.split("\n")[0] if func.__doc__ else None
        )

        # Create the rule class inheriting from Rule.
        rule_class = type(
            func.__name__,
            (Rule,),
            {
                "description": rule_description,
                "severity": severity,
                "evaluate": func,
            },
        )

        return rule_class

    return decorator_rule
