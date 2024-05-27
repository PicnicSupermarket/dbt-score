"""Formatter for a manifest.json."""

import copy
import json
from typing import Any

from dbt_score.evaluation import ModelResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Model


class ManifestFormatter(Formatter):
    """Formatter to generate manifest.json with score metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Instantiate a manifest formatter."""
        self._model_scores: dict[str, float] = {}
        super().__init__(*args, **kwargs)

    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: float
    ) -> None:
        """Callback when a model has been evaluated."""
        self._model_scores[model.unique_id] = score

    def project_evaluated(self, score: float) -> None:
        """Callback when a project has been evaluated."""
        manifest = copy.copy(self._manifest_loader.raw_manifest)
        for model_id, score in self._model_scores.items():
            manifest["nodes"][model_id]["meta"]["score"] = round(score, 1)
        print(json.dumps(manifest, indent=2))
