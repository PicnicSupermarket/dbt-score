"""Formatters are used to output CLI results."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from dbt_score.scoring import Score

if typing.TYPE_CHECKING:
    from dbt_score.evaluation import ModelResultsType
from dbt_score.models import ManifestLoader, Model


class Formatter(ABC):
    """Abstract class to define a formatter."""

    def __init__(self, manifest_loader: ManifestLoader):
        """Instantiate a formatter."""
        self._manifest_loader = manifest_loader

    @abstractmethod
    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: Score
    ) -> None:
        """Callback when a model has been evaluated."""
        raise NotImplementedError

    @abstractmethod
    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        raise NotImplementedError
