"""Vendored utility functions from https://github.com/more-itertools/more-itertools."""

from collections.abc import Callable, Iterable
from typing import (
    TypeVar,
    overload,
)

_T = TypeVar("_T")
_U = TypeVar("_U")


@overload
def first_true(
    iterable: Iterable[_T], *, pred: Callable[[_T], object] | None = ...
) -> _T | None: ...


@overload
def first_true(
    iterable: Iterable[_T],
    default: _U,
    pred: Callable[[_T], object] | None = ...,
) -> _T | _U: ...


def first_true(
    iterable: Iterable[_T],
    default: _U | None = None,
    pred: Callable[[_T], object] | None = None,
) -> _T | _U | None:
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item for which
    ``pred(item) == True`` .

        >>> first_true(range(10))
        1
        >>> first_true(range(10), pred=lambda x: x > 5)
        6
        >>> first_true(range(10), default='missing', pred=lambda x: x > 9)
        'missing'

    """
    return next(filter(pred, iterable), default)
