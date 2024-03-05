"""dbt-score definitions."""


from functools import wraps
from typing import Any, Callable


def rule(func: Callable[..., None]) -> Callable[..., None]:
    """Wrapper to create a rule."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    wrapper._is_rule = True  # type: ignore
    return wrapper
