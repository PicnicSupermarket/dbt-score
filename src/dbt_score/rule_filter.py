"""Evaluable filtering to choose when to apply specific rules."""

import inspect
import typing
from typing import Any, Callable, Type, TypeAlias, cast, overload

from dbt_score.models import Evaluable, Model, Source
from dbt_score.more_itertools import first_true

ModelFilterEvaluationType: TypeAlias = Callable[[Model], bool]
SourceFilterEvaluationType: TypeAlias = Callable[[Source], bool]
FilterEvaluationType: TypeAlias = ModelFilterEvaluationType | SourceFilterEvaluationType


class RuleFilter:
    """The Filter base class."""

    description: str
    resource_type: typing.ClassVar[type[Evaluable]]

    def __init__(self) -> None:
        """Initialize the filter."""
        pass

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore
        """Initializes the subclass."""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "description"):
            raise AttributeError("Subclass must define class attribute `description`.")

        cls.resource_type = cls._introspect_resource_type()

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

    def evaluate(self, evaluable: Evaluable) -> bool:
        """Evaluates the filter."""
        raise NotImplementedError("Subclass must implement method `evaluate`.")

    @classmethod
    def source(cls) -> str:
        """Return the source of the filter, i.e. a fully qualified name."""
        return f"{cls.__module__}.{cls.__name__}"

    def __hash__(self) -> int:
        """Compute a unique hash for a filter."""
        return hash(self.source())


# Use @overload to have proper typing for both @rule_filter and @rule_filter(...)
# https://mypy.readthedocs.io/en/stable/generics.html#decorator-factories


@overload
def rule_filter(__func: ModelFilterEvaluationType) -> Type[RuleFilter]:
    ...


@overload
def rule_filter(__func: SourceFilterEvaluationType) -> Type[RuleFilter]:
    ...


@overload
def rule_filter(
    *,
    description: str | None = None,
) -> Callable[[FilterEvaluationType], Type[RuleFilter]]:
    ...


def rule_filter(
    __func: FilterEvaluationType | None = None,
    *,
    description: str | None = None,
) -> Type[RuleFilter] | Callable[[FilterEvaluationType], Type[RuleFilter]]:
    """Rule-filter decorator.

    The rule_filter decorator creates a filter class (subclass of RuleFilter)
    and returns it.

    Using arguments or not are both supported:
    - ``@rule_filter``
    - ``@rule_filter(description="...")``

    Args:
        __func: The filter evaluation function being decorated.
        description: The description of the filter.
    """

    def decorator_filter(func: FilterEvaluationType) -> Type[RuleFilter]:
        """Decorator function."""
        if func.__doc__ is None and description is None:
            raise AttributeError(
                "RuleFilter must define `description` or `func.__doc__`."
            )

        # Get description parameter, otherwise use the docstring
        filter_description = description or (
            func.__doc__.split("\n")[0] if func.__doc__ else None
        )

        def wrapped_func(self: RuleFilter, *args: Any, **kwargs: Any) -> bool:
            """Wrap func to add `self`."""
            return func(*args, **kwargs)

        # Create the filter class inheriting from RuleFilter
        filter_class = type(
            func.__name__,
            (RuleFilter,),
            {
                "description": filter_description,
                "evaluate": wrapped_func,
                # Save provided evaluate function
                "_orig_evaluate": func,
                # Forward origin of the decorated function
                "__qualname__": func.__qualname__,  # https://peps.python.org/pep-3155/
                "__module__": func.__module__,
            },
        )

        return filter_class

    if __func is not None:
        # The syntax @rule_filter is used
        return decorator_filter(__func)
    else:
        # The syntax @rule_filter(...) is used
        return decorator_filter
