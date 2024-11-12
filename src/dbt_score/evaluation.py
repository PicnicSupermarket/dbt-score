"""This module is responsible for evaluating rules."""

from __future__ import annotations

from itertools import chain
from typing import Type, cast

from dbt_score.formatters import Formatter
from dbt_score.models import Evaluable, ManifestLoader
from dbt_score.rule import Rule, RuleViolation
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Score, Scorer

# The results of a given evaluable are stored in a dictionary, mapping rules to either:
# - None if there was no issue
# - A RuleViolation if a linting error was found
# - An Exception if the rule failed to run
EvaluableResultsType = dict[Type[Rule], None | RuleViolation | Exception]


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
            manifest_loader: A manifest loader to access dbt metadata.
            formatter: A formatter to display results.
            scorer: A scorer to compute scores.
        """
        self._rule_registry = rule_registry
        self._manifest_loader = manifest_loader
        self._formatter = formatter
        self._scorer = scorer

        # For each evaluable, its results
        self.results: dict[Evaluable, EvaluableResultsType] = {}

        # For each evaluable, its computed score
        self.scores: dict[Evaluable, Score] = {}

        # The aggregated project score
        self.project_score: Score

    def evaluate(self) -> None:
        """Evaluate all rules."""
        rules = self._rule_registry.rules.values()

        for evaluable in chain(
            self._manifest_loader.models, self._manifest_loader.sources
        ):
            # type inference on elements from `chain` is wonky
            # and resolves to superclass HasColumnsMixin
            evaluable = cast(Evaluable, evaluable)
            self.results[evaluable] = {}
            for rule in rules:
                try:
                    if rule.should_evaluate(evaluable):
                        result = rule.evaluate(evaluable, **rule.config)
                        self.results[evaluable][rule.__class__] = result
                except Exception as e:
                    self.results[evaluable][rule.__class__] = e

            self.scores[evaluable] = self._scorer.score_evaluable(
                self.results[evaluable]
            )
            self._formatter.evaluable_evaluated(
                evaluable, self.results[evaluable], self.scores[evaluable]
            )

        # Compute score for project
        self.project_score = self._scorer.score_aggregate_evaluables(
            list(self.scores.values())
        )

        # Add null check before calling project_evaluated
        if self._manifest_loader.models or self._manifest_loader.sources:
            self._formatter.project_evaluated(self.project_score)
