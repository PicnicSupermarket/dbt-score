"""Formatters are used to output CLI results."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from dbt_score.config import Config
from dbt_score.scoring import Score

if typing.TYPE_CHECKING:
    from dbt_score.evaluation import EvaluableResultsType
from dbt_score.models import Evaluable, ManifestLoader


class Formatter(ABC):
    """Abstract class to define a formatter."""

    def __init__(self, manifest_loader: ManifestLoader, config: Config):
        """Instantiate a formatter."""
        self._manifest_loader = manifest_loader
        self._config = config

    @abstractmethod
    def evaluable_evaluated(
        self, evaluable: Evaluable, results: EvaluableResultsType, score: Score
    ) -> None:
        """Callback when an evaluable item has been evaluated."""
        raise NotImplementedError

    @abstractmethod
    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        raise NotImplementedError
