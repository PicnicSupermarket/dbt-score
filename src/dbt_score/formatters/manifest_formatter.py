"""Formatter for a manifest.json."""

import copy
import json
from typing import Any

from dbt_score.evaluation import EvaluableResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Evaluable
from dbt_score.scoring import Score


class ManifestFormatter(Formatter):
    """Formatter to generate manifest.json with score metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Instantiate a manifest formatter."""
        self._evaluable_scores: dict[str, Score] = {}
        super().__init__(*args, **kwargs)

    def evaluable_evaluated(
        self, evaluable: Evaluable, results: EvaluableResultsType, score: Score
    ) -> None:
        """Callback when an evaluable item has been evaluated."""
        self._evaluable_scores[evaluable.unique_id] = score

    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        manifest = copy.copy(self._manifest_loader.raw_manifest)
        for evaluable_id, evaluable_score in self._evaluable_scores.items():
            if evaluable_id.startswith("model"):
                model_manifest = manifest["nodes"][evaluable_id]
                model_manifest["meta"]["score"] = evaluable_score.value
                model_manifest["meta"]["badge"] = evaluable_score.badge
            if evaluable_id.startswith("source"):
                source_manifest = manifest["sources"][evaluable_id]
                source_manifest["meta"]["score"] = evaluable_score.value
                source_manifest["meta"]["badge"] = evaluable_score.badge
        print(json.dumps(manifest, indent=2))
