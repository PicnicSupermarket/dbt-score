"""Module computing scores."""

from __future__ import annotations

import typing

from dbt_score.config import Config

if typing.TYPE_CHECKING:
    from dbt_score.evaluation import ModelResultsType
from dbt_score.rule import RuleViolation, Severity


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
        self.bronze_medal_threshold = config.bronze_medal_threshold
        self.silver_medal_threshold = config.silver_medal_threshold
        self.gold_medal_threshold = config.gold_medal_threshold

    def score_model(self, model_results: ModelResultsType) -> float:
        """Compute the score of a given model."""
        if len(model_results) == 0:
            # No rule? No problem
            return self.max_score
        if any(
                rule.severity == Severity.CRITICAL and isinstance(result, RuleViolation)
                for rule, result in model_results.items()
        ):
            # If there's a CRITICAL violation, the score is 0
            return self.min_score
        else:
            # Otherwise, the score is the weighted average (by severity) of the results
            return (
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

    def score_aggregate_models(self, scores: list[float]) -> float:
        """Compute the score of a list of models."""
        if 0.0 in scores:
            # Any model with a CRITICAL violation makes the project score 0
            return self.min_score
        if len(scores) == 0:
            return self.max_score
        return sum(scores) / len(scores)

    def award_medal(self, score: float) -> str:
        """Award a medal based on a score."""
        rounded_score = round(score, 1)
        if rounded_score >= self.gold_medal_threshold:
            return "🥇"
        elif rounded_score >= self.silver_medal_threshold:
            return "🥈"
        elif rounded_score >= self.bronze_medal_threshold:
            return "🥉"
        else:
            return ""
