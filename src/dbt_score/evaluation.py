"""This module is responsible for evaluating rules."""

from __future__ import annotations

from typing import Type

from dbt_score.formatters import Formatter
from dbt_score.models import ManifestLoader, Model
from dbt_score.rule import Rule, RuleViolation, Severity
from dbt_score.rule_registry import RuleRegistry

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
    ) -> None:
        """Create an Evaluation object.

        Args:
            rule_registry: A rule registry.
            manifest_loader: A manifest loader.
            formatter: A formatter.
        """
        self._rule_registry = rule_registry
        self._manifest_loader = manifest_loader
        self._formatter = formatter

        # For each model, its results
        self.results: dict[Model, ModelResultsType] = {}

        # For each model, its computed score
        self.scores: dict[Model, float] = {}

        # The aggregated project score
        self.project_score: float

    def evaluate(self) -> None:
        """Evaluate all rules."""
        # Instantiate all rules. In case they keep state across calls, this must be
        # done only once.
        rules = [rule_class() for rule_class in self._rule_registry.rules.values()]

        for model in self._manifest_loader.models:
            self.results[model] = {}
            for rule in rules:
                try:
                    result = rule.evaluate(model)
                except Exception as e:
                    self.results[model][rule.__class__] = e
                else:
                    if result is None:
                        self.results[model][rule.__class__] = None
                    else:
                        self.results[model][rule.__class__] = result

            self.scores[model] = self.score_model(model)
            self._formatter.model_evaluated(
                model, self.results[model], self.scores[model]
            )

        # Compute score for project
        self.project_score = self.score_project()
        self._formatter.project_evaluated(self.project_score)

    def score_model(self, model: Model) -> float:
        """Compute the score of a given model."""
        model_results = self.results[model]

        if len(model_results) == 0:
            # No rule? No problem
            return 1.0
        if any(
            rule.severity == Severity.CRITICAL and isinstance(result, RuleViolation)
            for rule, result in model_results.items()
        ):
            # If there's a CRITICAL violation, the score is 0
            return 0.0
        else:
            # Otherwise, the score is the weighted average (by severity) of the results
            return sum(
                [
                    # The more severe the violation, the more points are lost
                    3 - rule.severity.value if isinstance(result, RuleViolation) else 3
                    for rule, result in model_results.items()
                ]
            ) / (3 * len(model_results))

    def score_project(self) -> float:
        """Compute the aggregated score for the project."""
        if len(self.scores) == 0:
            return 1.0
        return sum(self.scores.values()) / len(self.scores)
