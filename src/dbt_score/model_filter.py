"""Model filtering to choose when to apply specific rules."""
import inspect
import typing
from typing import Any, Callable, Type, TypeAlias, overload

from more_itertools import first_true

from dbt_score.models import Evaluable

FilterEvaluationType: TypeAlias = Callable[[Evaluable], bool]


class ModelFilter:
    """The Filter base class."""

    description: str
    resource_type: typing.ClassVar[Evaluable]

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
                "Subclass must implement method `evaluate` with an annotated Model or Source argument."
            )

        return resource_type_argument.annotation

    def evaluate(self, model: Evaluable) -> bool:
        """Evaluates the filter."""
        raise NotImplementedError("Subclass must implement method `evaluate`.")

    @classmethod
    def source(cls) -> str:
        """Return the source of the filter, i.e. a fully qualified name."""
        return f"{cls.__module__}.{cls.__name__}"

    def __hash__(self) -> int:
        """Compute a unique hash for a filter."""
        return hash(self.source())


# Use @overload to have proper typing for both @model_filter and @model_filter(...)
# https://mypy.readthedocs.io/en/stable/generics.html#decorator-factories


@overload
def model_filter(__func: FilterEvaluationType) -> Type[ModelFilter]:
    ...


@overload
def model_filter(
    *,
    description: str | None = None,
) -> Callable[[FilterEvaluationType], Type[ModelFilter]]:
    ...


def model_filter(
    __func: FilterEvaluationType | None = None,
    *,
    description: str | None = None,
) -> Type[ModelFilter] | Callable[[FilterEvaluationType], Type[ModelFilter]]:
    """Model-filter decorator.

    The model-filter decorator creates a filter class (subclass of ModelFilter)
    and returns it.

    Using arguments or not are both supported:
    - ``@model_filter``
    - ``@model_filter(description="...")``

    Args:
        __func: The filter evaluation function being decorated.
        description: The description of the filter.
    """

    def decorator_filter(
        func: FilterEvaluationType,
    ) -> Type[ModelFilter]:
        """Decorator function."""
        if func.__doc__ is None and description is None:
            raise AttributeError(
                "ModelFilter must define `description` or `func.__doc__`."
            )

        # Get description parameter, otherwise use the docstring
        filter_description = description or (
            func.__doc__.split("\n")[0] if func.__doc__ else None
        )

        def wrapped_func(self: ModelFilter, *args: Any, **kwargs: Any) -> bool:
            """Wrap func to add `self`."""
            return func(*args, **kwargs)

        # Create the filter class inheriting from ModelFilter
        filter_class = type(
            func.__name__,
            (ModelFilter,),
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
        # The syntax @model_filter is used
        return decorator_filter(__func)
    else:
        # The syntax @model_filter(...) is used
        return decorator_filter
