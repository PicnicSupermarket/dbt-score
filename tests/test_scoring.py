"""Unit tests for the scoring module."""


from dbt_score.rule import RuleViolation
from dbt_score.scoring import Scorer


def test_scorer_model_no_results():
    """Test scorer with a model without any result."""
    scorer = Scorer()
    assert scorer.score_model({}) == 10.0


def test_scorer_model_severity_low(rule_severity_low):
    """Test scorer with a model and one low severity rule."""
    scorer = Scorer()
    assert scorer.score_model({rule_severity_low: None}) == 10.0
    assert scorer.score_model({rule_severity_low: Exception()}) == 10.0
    assert (
        round(scorer.score_model({rule_severity_low: RuleViolation("error")}), 2)
        == 6.67
    )


def test_scorer_model_severity_medium(rule_severity_medium):
    """Test scorer with a model and one medium severity rule."""
    scorer = Scorer()
    assert scorer.score_model({rule_severity_medium: None}) == 10.0
    assert scorer.score_model({rule_severity_medium: Exception()}) == 10.0
    assert (
        round(scorer.score_model({rule_severity_medium: RuleViolation("error")}), 2)
        == 3.33
    )


def test_scorer_model_severity_high(rule_severity_high):
    """Test scorer with a model and one high severity rule."""
    scorer = Scorer()
    assert scorer.score_model({rule_severity_high: None}) == 10.0
    assert scorer.score_model({rule_severity_high: Exception()}) == 10.0
    assert scorer.score_model({rule_severity_high: RuleViolation("error")}) == 0.0


def test_scorer_model_severity_critical(rule_severity_critical):
    """Test scorer with a model and one critical severity rule."""
    scorer = Scorer()
    assert scorer.score_model({rule_severity_critical: None}) == 10.0
    assert scorer.score_model({rule_severity_critical: Exception()}) == 10.0
    assert scorer.score_model({rule_severity_critical: RuleViolation("error")}) == 0.0


def test_scorer_model_severity_critical_overwrites(
    rule_severity_low, rule_severity_critical
):
    """Test scorer with a model and multiple rules including one critical."""
    scorer = Scorer()
    assert (
        scorer.score_model(
            {rule_severity_low: None, rule_severity_critical: RuleViolation("error")}
        )
        == 0.0
    )


def test_scorer_model_multiple_rules(
    rule_severity_low, rule_severity_medium, rule_severity_high
):
    """Test scorer with a model and multiple rules."""
    scorer = Scorer()
    assert (
        round(
            scorer.score_model(
                {
                    rule_severity_low: None,
                    rule_severity_medium: Exception(),
                    rule_severity_high: RuleViolation("error"),
                }
            ),
            2,
        )
        == 6.67
    )

    assert (
        round(
            scorer.score_model(
                {
                    rule_severity_low: Exception(),
                    rule_severity_medium: RuleViolation("error"),
                    rule_severity_high: None,
                }
            ),
            2,
        )
        == 7.78
    )

    assert (
        round(
            scorer.score_model(
                {
                    rule_severity_low: RuleViolation("error"),
                    rule_severity_medium: Exception(),
                    rule_severity_high: None,
                }
            ),
            2,
        )
        == 8.89
    )


def test_scorer_aggregate_empty():
    """Test scorer aggregation with no results."""
    scorer = Scorer()
    assert scorer.score_aggregate_models([]) == 10.0


def test_scorer_aggregate_with_0():
    """Test scorer aggregation with one result that is 0.0."""
    scorer = Scorer()
    assert scorer.score_aggregate_models([1.0, 5.0, 0.0]) == 0.0


def test_scorer_aggregate_single():
    """Test scorer aggregation with a single results."""
    scorer = Scorer()
    assert scorer.score_aggregate_models([4.2]) == 4.2


def test_scorer_aggregate_multiple():
    """Test scorer aggregation with multiple results."""
    scorer = Scorer()
    assert scorer.score_aggregate_models([1.0, 1.0, 1.0]) == 1.0
    assert scorer.score_aggregate_models([0.0, 0.0, 0.0]) == 0.0
    assert scorer.score_aggregate_models([1.0, 7.4, 4.2]) == 4.2
