"""Formatter for a manifest.json."""

import copy
import json
from typing import Any, TypedDict

from dbt_score.evaluation import ModelResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Model


class ManifestFormatter(Formatter):
    """Formatter to generate manifest.json with score metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Instantiate a manifest formatter."""
        result_dict = TypedDict("result_dict", {"score": float, "medal": str})
        self._model_results: dict[str, result_dict] = {}
        super().__init__(*args, **kwargs)

    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: float, medal: str
    ) -> None:
        """Callback when a model has been evaluated."""
        self._model_results[model.unique_id] = {"score": score, "medal": medal}

    def project_evaluated(self, score: float, medal: str) -> None:
        """Callback when a project has been evaluated."""
        manifest = copy.copy(self._manifest_loader.raw_manifest)
        for model_id, results in self._model_results.items():
            manifest["nodes"][model_id]["meta"]["score"] = round(results["score"], 1)
            manifest["nodes"][model_id]["meta"]["medal"] = results["medal"]
        print(json.dumps(manifest, indent=2))
