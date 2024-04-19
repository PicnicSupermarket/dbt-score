"""Formatters are used to output CLI results."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from dbt_score.evaluation import ModelResultsType
from dbt_score.models import Model


class Formatter(ABC):
    """Abstract class to define a formatter."""

    @abstractmethod
    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: float
    ) -> None:
        """Callback when a model has been evaluated."""
        raise NotImplementedError

    @abstractmethod
    def project_evaluated(self, score: float) -> None:
        """Callback when a project has been evaluated."""
        raise NotImplementedError
