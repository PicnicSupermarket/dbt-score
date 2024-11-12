"""Rule definitions."""

import inspect
import typing
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Iterable,
    Type,
    TypeAlias,
    cast,
    overload,
)

from dbt_score.models import Evaluable, Model, Source
from dbt_score.more_itertools import first_true
from dbt_score.rule_filter import RuleFilter


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
    rule_filter_names: list[str] = field(default_factory=list)

    @staticmethod
    def from_dict(rule_config: dict[str, Any]) -> "RuleConfig":
        """Create a RuleConfig from a dictionary."""
        config = rule_config.copy()
        severity = (
            Severity(config.pop("severity", None))
            if "severity" in rule_config
            else None
        )
        filter_names = (
            config.pop("rule_filter_names", None)
            if "rule_filter_names" in rule_config
            else []
        )

        return RuleConfig(
            severity=severity, config=config, rule_filter_names=filter_names
        )


@dataclass
class RuleViolation:
    """The violation of a rule."""

    message: str | None = None


ModelRuleEvaluationType: TypeAlias = Callable[[Model], RuleViolation | None]
SourceRuleEvaluationType: TypeAlias = Callable[[Source], RuleViolation | None]
RuleEvaluationType: TypeAlias = ModelRuleEvaluationType | SourceRuleEvaluationType


class Rule:
    """The rule base class."""

    description: str
    severity: Severity = Severity.MEDIUM
    rule_filter_names: list[str]
    rule_filters: frozenset[RuleFilter] = frozenset()
    default_config: typing.ClassVar[dict[str, Any]] = {}
    resource_type: typing.ClassVar[type[Evaluable]]

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

        cls.resource_type = cls._introspect_resource_type()

        cls._validate_rule_filters()

    @classmethod
    def _validate_rule_filters(cls) -> None:
        for rule_filter in cls.rule_filters:
            if rule_filter.resource_type != cls.resource_type:
                raise TypeError(
                    f"Mismatched resource_type on filter "
                    f"{rule_filter.__class__.__name__}. "
                    f"Expected {cls.resource_type.__name__}, "
                    f"but got {rule_filter.resource_type.__name__}."
                )

    @classmethod
    def _introspect_resource_type(cls) -> Type[Evaluable]:
        evaluate_func = getattr(cls, "_orig_evaluate", cls.evaluate)

        sig = inspect.signature(evaluate_func)
        resource_type_argument = first_true(
            sig.parameters.values(),
            pred=lambda arg: arg.annotation in typing.get_args(Evaluable),
        )

        if not resource_type_argument:
            raise TypeError(
                "Subclass must implement method `evaluate` with an "
                "annotated Model or Source argument."
            )

        resource_type = cast(type[Evaluable], resource_type_argument.annotation)
        return resource_type

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
        self.rule_filter_names = rule_config.rule_filter_names
        self.config = config

    def evaluate(self, evaluable: Evaluable) -> RuleViolation | None:
        """Evaluates the rule."""
        raise NotImplementedError("Subclass must implement method `evaluate`.")

    @classmethod
    def should_evaluate(cls, evaluable: Evaluable) -> bool:
        """Checks whether the rule should be applied against the evaluable.

        The evaluable must satisfy the following criteria:
            - all filters in the rule allow evaluation
            - the rule and evaluable have matching resource_types
        """
        resource_types_match = cls.resource_type is type(evaluable)

        if cls.rule_filters:
            return (
                all(f.evaluate(evaluable) for f in cls.rule_filters)
                and resource_types_match
            )
        return resource_types_match

    @classmethod
    def set_severity(cls, severity: Severity) -> None:
        """Set the severity of the rule."""
        cls.severity = severity

    @classmethod
    def set_filters(cls, rule_filters: Iterable[RuleFilter]) -> None:
        """Set the filters of the rule."""
        cls.rule_filters = frozenset(rule_filters)

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
def rule(__func: ModelRuleEvaluationType) -> Type[Rule]:
    ...


@overload
def rule(__func: SourceRuleEvaluationType) -> Type[Rule]:
    ...


@overload
def rule(
    *,
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
    rule_filters: set[RuleFilter] | None = None,
) -> Callable[[RuleEvaluationType], Type[Rule]]:
    ...


def rule(
    __func: RuleEvaluationType | None = None,
    *,
    description: str | None = None,
    severity: Severity = Severity.MEDIUM,
    rule_filters: set[RuleFilter] | None = None,
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
        rule_filters: Set of RuleFilter that filters the items that the rule applies to.
    """

    def decorator_rule(func: RuleEvaluationType) -> Type[Rule]:
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
                "rule_filters": rule_filters or frozenset(),
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
