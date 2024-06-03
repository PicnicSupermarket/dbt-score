"""Module computing scores."""

from __future__ import annotations

import typing
from dataclasses import dataclass

from dbt_score.config import Config

if typing.TYPE_CHECKING:
    from dbt_score.evaluation import ModelResultsType
from dbt_score.rule import RuleViolation, Severity


@dataclass
class Score:
    """Class representing a score."""

    value: float
    badge: str


class Scorer:
    """Logic for computing scores."""

    # This magic number comes from rule severity.
    # Assuming a rule violation:
    # - A low severity yields a score 2/3
    # - A medium severity yields a score 1/3
    # - A high severity yields a score 0/3
    score_cardinality = 3

    min_score = 0.0
    max_score = 10.0

    def __init__(self, config: Config) -> None:
        """Create a Scorer object."""
        self._config = config

    def score_model(self, model_results: ModelResultsType) -> Score:
        """Compute the score of a given model."""
        if len(model_results) == 0:
            # No rule? No problem
            score = self.max_score
        elif any(
            rule.severity == Severity.CRITICAL and isinstance(result, RuleViolation)
            for rule, result in model_results.items()
        ):
            # If there's a CRITICAL violation, the score is 0
            score = self.min_score
        else:
            # Otherwise, the score is the weighted average (by severity) of the results
            score = (
                sum(
                    [
                        # The more severe the violation, the more points are lost
                        self.score_cardinality - rule.severity.value
                        if isinstance(result, RuleViolation)  # Either 0/3, 1/3 or 2/3
                        else self.score_cardinality  # 3/3
                        for rule, result in model_results.items()
                    ]
                )
                / (self.score_cardinality * len(model_results))
                * self.max_score
            )

        return Score(score, self._badge(score))

    def score_aggregate_models(self, scores: list[Score]) -> Score:
        """Compute the score of a list of models."""
        actual_scores = [s.value for s in scores]
        if 0.0 in actual_scores:
            # Any model with a CRITICAL violation makes the project score 0
            score = Score(self.min_score, self._badge(self.min_score))
        elif len(actual_scores) == 0:
            score = Score(self.max_score, self._badge(self.max_score))
        else:
            average_score = sum(actual_scores) / len(actual_scores)
            score = Score(average_score, self._badge(average_score))
        return score

    def _badge(self, score: float) -> str:
        """Compute the badge of a given score."""
        if score >= self._config.badge_config.first.threshold:
            return self._config.badge_config.first.icon
        elif score >= self._config.badge_config.second.threshold:
            return self._config.badge_config.second.icon
        elif score >= self._config.badge_config.third.threshold:
            return self._config.badge_config.third.icon
        else:
            return self._config.badge_config.wip.icon
