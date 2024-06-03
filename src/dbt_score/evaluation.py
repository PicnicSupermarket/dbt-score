"""This module is responsible for evaluating rules."""

from __future__ import annotations

from typing import Type

from dbt_score.formatters import Formatter
from dbt_score.models import ManifestLoader, Model
from dbt_score.rule import Rule, RuleViolation
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Score, Scorer

# The results of a given model are stored in a dictionary, mapping rules to either:
# - None if there was no issue
# - A RuleViolation if a linting error was found
# - An Exception if the rule failed to run
ModelResultsType = dict[Type[Rule], None | RuleViolation | Exception]


class Evaluation:
    """Evaluate a set of rules on a set of nodes."""

    def __init__(
        self,
        rule_registry: RuleRegistry,
        manifest_loader: ManifestLoader,
        formatter: Formatter,
        scorer: Scorer,
    ) -> None:
        """Create an Evaluation object.

        Args:
            rule_registry: A rule registry to access rules.
            manifest_loader: A manifest loader to access model metadata.
            formatter: A formatter to display results.
            scorer: A scorer to compute scores.
        """
        self._rule_registry = rule_registry
        self._manifest_loader = manifest_loader
        self._formatter = formatter
        self._scorer = scorer

        # For each model, its results
        self.results: dict[Model, ModelResultsType] = {}

        # For each model, its computed score
        self.scores: dict[Model, Score] = {}

        # The aggregated project score
        self.project_score: Score

    def evaluate(self) -> None:
        """Evaluate all rules."""
        rules = self._rule_registry.rules.values()

        for model in self._manifest_loader.models:
            self.results[model] = {}
            for rule in rules:
                try:
                    result: RuleViolation | None = rule.evaluate(model, **rule.config)
                except Exception as e:
                    self.results[model][rule.__class__] = e
                else:
                    self.results[model][rule.__class__] = result

            self.scores[model] = self._scorer.score_model(self.results[model])
            self._formatter.model_evaluated(
                model, self.results[model], self.scores[model]
            )

        # Compute score for project
        self.project_score = self._scorer.score_aggregate_models(
            list(self.scores.values())
        )
        self._formatter.project_evaluated(self.project_score)
