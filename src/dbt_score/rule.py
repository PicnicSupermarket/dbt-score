"""Rule definitions."""

import inspect
import typing
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Type, TypeAlias, overload

from dbt_score.models import Model


class Severity(Enum):
    """The severity/weight of a rule."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RuleConfig:
    """Configuration for a rule."""

    severity: Severity | None = None
    config: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(rule_config: dict[str, Any]) -> "RuleConfig":
        """Create a RuleConfig from a dictionary."""
        config = rule_config.copy()
        severity = (
            Severity(config.pop("severity", None))
            if "severity" in rule_config
            else None
        )

        return RuleConfig(severity=severity, config=config)


@dataclass
class RuleViolation:
    """The violation of a rule."""

    message: str | None = None


RuleEvaluationType: TypeAlias = Callable[[Model], RuleViolation | None]


class Rule:
    """The rule base class."""

    description: str
    severity: Severity = Severity.MEDIUM
    default_config: typing.ClassVar[dict[str, Any]] = {}

    def __init__(self, rule_config: RuleConfig | None = None) -> None:
        """Initialize the rule."""
        self.config: dict[str, Any] = {}
        if rule_config:
            self.process_config(rule_config)

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore
        """Initializes the subclass."""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "description"):
            raise AttributeError("Subclass must define class attribute `description`.")

    def process_config(self, rule_config: RuleConfig) -> None:
        """Process the rule config."""
        config = self.default_config.copy()

        # Overwrite default rule configuration
        for k, v in rule_config.config.items():
            if k in self.default_config:
                config[k] = v
            else:
                raise AttributeError(
                    f"Unknown rule parameter: {k} for rule {self.source()}."
                )

        self.set_severity(
            rule_config.severity
        ) if rule_config.severity else rule_config.severity
        self.config = config

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluates the rule."""
        raise NotImplementedError("Subclass must implement method `evaluate`.")

    @classmethod
    def set_severity(cls, severity: Severity) -> None:
        """Set the severity of the rule."""
        cls.severity = severity

    @classmethod
    def source(cls) -> str:
        """Return the source of the rule, i.e. a fully qualified name."""
        return f"{cls.__module__}.{cls.__name__}"

    def __hash__(self) -> int:
        """Compute a unique hash for a rule."""
        return hash(self.source())


# Use @overload to have proper typing for both @rule and @rule(...)
# https://mypy.readthedocs.io/en/stable/generics.html#decorator-factories


@overload
def rule(__func: RuleEvaluationType) -> Type[Rule]:
    ...


@overload
def rule(
    *,
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
) -> Callable[[RuleEvaluationType], Type[Rule]]:
    ...


def rule(
    __func: RuleEvaluationType | None = None,
    *,
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
) -> Type[Rule] | Callable[[RuleEvaluationType], Type[Rule]]:
    """Rule decorator.

    The rule decorator creates a rule class (subclass of Rule) and returns it.

    Using arguments or not are both supported:
    - ``@rule``
    - ``@rule(description="...")``

    Args:
        __func: The rule evaluation function being decorated.
        description: The description of the rule.
        severity: The severity of the rule.
    """

    def decorator_rule(
        func: RuleEvaluationType,
    ) -> Type[Rule]:
        """Decorator function."""
        if func.__doc__ is None and description is None:
            raise AttributeError("Rule must define `description` or `func.__doc__`.")

        # Get description parameter, otherwise use the docstring
        rule_description = description or (
            func.__doc__.split("\n")[0] if func.__doc__ else None
        )

        def wrapped_func(self: Rule, *args: Any, **kwargs: Any) -> RuleViolation | None:
            """Wrap func to add `self`."""
            return func(*args, **kwargs)

        # Get default parameters from the rule definition
        default_config = {
            key: val.default
            for key, val in inspect.signature(func).parameters.items()
            if val.default != inspect.Parameter.empty
        }

        # Create the rule class inheriting from Rule
        rule_class = type(
            func.__name__,
            (Rule,),
            {
                "description": rule_description,
                "severity": severity,
                "default_config": default_config,
                "evaluate": wrapped_func,
                # Save provided evaluate function
                "_orig_evaluate": func,
                # Forward origin of the decorated function
                "__qualname__": func.__qualname__,  # https://peps.python.org/pep-3155/
                "__module__": func.__module__,
            },
        )

        return rule_class

    if __func is not None:
        # The syntax @rule is used
        return decorator_rule(__func)
    else:
        # The syntax @rule(...) is used
        return decorator_rule
