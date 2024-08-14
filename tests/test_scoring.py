"""Unit tests for the scoring module."""


from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score, Scorer


def test_scorer_model_no_results(default_config):
    """Test scorer with a model without any result."""
    scorer = Scorer(config=default_config)
    assert scorer.score_model({}).value == 10.0


def test_scorer_model_severity_low(default_config, rule_severity_low):
    """Test scorer with a model and one low severity rule."""
    scorer = Scorer(config=default_config)
    assert scorer.score_model({rule_severity_low: None}).value == 10.0
    assert scorer.score_model({rule_severity_low: Exception()}).value == 10.0
    assert (
        round(scorer.score_model({rule_severity_low: RuleViolation("error")}).value, 2)
        == 6.67
    )


def test_scorer_model_severity_medium(default_config, rule_severity_medium):
    """Test scorer with a model and one medium severity rule."""
    scorer = Scorer(config=default_config)
    assert scorer.score_model({rule_severity_medium: None}).value == 10.0
    assert scorer.score_model({rule_severity_medium: Exception()}).value == 10.0
    assert (
        round(
            scorer.score_model({rule_severity_medium: RuleViolation("error")}).value, 2
        )
        == 3.33
    )


def test_scorer_model_severity_high(default_config, rule_severity_high):
    """Test scorer with a model and one high severity rule."""
    scorer = Scorer(config=default_config)
    assert scorer.score_model({rule_severity_high: None}).value == 10.0
    assert scorer.score_model({rule_severity_high: Exception()}).value == 10.0
    assert scorer.score_model({rule_severity_high: RuleViolation("error")}).value == 0.0


def test_scorer_model_severity_critical(default_config, rule_severity_critical):
    """Test scorer with a model and one critical severity rule."""
    scorer = Scorer(config=default_config)
    assert scorer.score_model({rule_severity_critical: None}).value == 10.0
    assert scorer.score_model({rule_severity_critical: Exception()}).value == 10.0
    assert (
        scorer.score_model({rule_severity_critical: RuleViolation("error")}).value
        == 0.0
    )


def test_scorer_model_severity_critical_overwrites(
    default_config, rule_severity_low, rule_severity_critical
):
    """Test scorer with a model and multiple rules including one critical."""
    scorer = Scorer(config=default_config)
    assert (
        scorer.score_model(
            {rule_severity_low: None, rule_severity_critical: RuleViolation("error")}
        ).value
        == 0.0
    )


def test_scorer_model_multiple_rules(
    default_config, rule_severity_low, rule_severity_medium, rule_severity_high
):
    """Test scorer with a model and multiple rules."""
    scorer = Scorer(config=default_config)
    assert (
        round(
            scorer.score_model(
                {
                    rule_severity_low: None,
                    rule_severity_medium: Exception(),
                    rule_severity_high: RuleViolation("error"),
                }
            ).value,
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
            ).value,
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
            ).value,
            2,
        )
        == 8.89
    )


def test_scorer_aggregate_empty(default_config):
    """Test scorer aggregation with no results."""
    scorer = Scorer(config=default_config)
    assert scorer.score_aggregate_models([]).value == 10.0


def test_scorer_aggregate_with_0(default_config):
    """Test scorer aggregation with one result that is 0.0."""
    scorer = Scorer(config=default_config)
    scores = [Score(1.0, ""), Score(5.0, ""), Score(0.0, "")]
    assert scorer.score_aggregate_models(scores).value == 0.0


def test_scorer_aggregate_single(default_config):
    """Test scorer aggregation with a single results."""
    scorer = Scorer(config=default_config)
    assert scorer.score_aggregate_models([Score(4.2, "")]).value == 4.2


def test_scorer_aggregate_multiple(default_config):
    """Test scorer aggregation with multiple results."""
    scorer = Scorer(config=default_config)
    assert (
        scorer.score_aggregate_models(
            [Score(1.0, ""), Score(1.0, ""), Score(1.0, "")]
        ).value
        == 1.0
    )
    assert (
        scorer.score_aggregate_models(
            [Score(1.0, ""), Score(7.4, ""), Score(4.2, "")]
        ).value
        == 4.2
    )
    assert (
        scorer.score_aggregate_models(
            [Score(0.0, ""), Score(0.0, ""), Score(0.0, "")]
        ).value
        == 0.0
    )


def test_scorer_badge(default_config):
    """Test scorer awarding a badge."""
    scorer = Scorer(config=default_config)
    assert scorer._badge(10.0) == scorer._config.badge_config.first.icon
    assert scorer._badge(8.0) == scorer._config.badge_config.second.icon
    assert scorer._badge(7.0) == scorer._config.badge_config.third.icon
    assert scorer._badge(1.0) == scorer._config.badge_config.wip.icon
