"""Unit tests for the evaluation module."""

from unittest.mock import Mock

from dbt_score.config import Config
from dbt_score.evaluation import Evaluation
from dbt_score.models import ManifestLoader
from dbt_score.rule import RuleViolation
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Score


def test_evaluation_low_medium_high(
    manifest_path,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_high,
    rule_error,
    default_config,
):
    """Test rule evaluation with a combination of LOW, MEDIUM and HIGH severity."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()
    mock_scorer = Mock()

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(rule_severity_low)
    rule_registry._add_rule(rule_severity_medium)
    rule_registry._add_rule(rule_severity_high)
    rule_registry._add_rule(rule_error)

    # Ensure we get a valid Score object from the Mock
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
    )
    evaluation.evaluate()

    model1 = manifest_loader.models[0]
    model2 = manifest_loader.models[1]

    assert evaluation.results[model1][rule_severity_low] is None
    assert evaluation.results[model1][rule_severity_medium] is None
    assert evaluation.results[model1][rule_severity_high] is None
    assert isinstance(evaluation.results[model1][rule_error], Exception)

    assert isinstance(evaluation.results[model2][rule_severity_low], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_medium], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_high], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_error], Exception)

    assert mock_formatter.model_evaluated.call_count == 2
    assert mock_formatter.project_evaluated.call_count == 1

    assert mock_scorer.score_model.call_count == 2
    assert mock_scorer.score_aggregate_models.call_count == 1


def test_evaluation_critical(
    manifest_path, rule_severity_low, rule_severity_critical, default_config
):
    """Test rule evaluation with a CRITICAL severity."""
    manifest_loader = ManifestLoader(manifest_path)

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(rule_severity_low)
    rule_registry._add_rule(rule_severity_critical)

    mock_formatter = Mock()
    mock_scorer = Mock()
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
    )

    evaluation.evaluate()

    model2 = manifest_loader.models[1]

    assert isinstance(evaluation.results[model2][rule_severity_critical], RuleViolation)


def test_evaluation_no_rule(manifest_path, default_config):
    """Test rule evaluation when no rule exists."""
    manifest_loader = ManifestLoader(manifest_path)

    rule_registry = RuleRegistry(default_config)

    mock_formatter = Mock()
    mock_scorer = Mock()
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
    )
    evaluation.evaluate()

    for results in evaluation.results.values():
        assert len(results) == 0


def test_evaluation_no_model(manifest_empty_path, rule_severity_low, default_config):
    """Test rule evaluation when no model exists."""
    manifest_loader = ManifestLoader(manifest_empty_path)

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(rule_severity_low)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=Mock(),
        scorer=Mock(),
    )
    evaluation.evaluate()

    assert len(evaluation.results) == 0
    assert list(evaluation.scores.values()) == []


def test_evaluation_no_model_no_rule(manifest_empty_path, default_config):
    """Test rule evaluation when no rule and no model exists."""
    manifest_loader = ManifestLoader(manifest_empty_path)

    rule_registry = RuleRegistry(default_config)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=Mock(),
        scorer=Mock(),
    )
    evaluation.evaluate()

    assert len(evaluation.results) == 0
    assert list(evaluation.scores.values()) == []


def test_evaluation_rule_with_config(
    manifest_path, rule_with_config, valid_config_path
):
    """Test rule evaluation with parameters."""
    manifest_loader = ManifestLoader(manifest_path)
    model1 = manifest_loader.models[0]
    model2 = manifest_loader.models[1]

    config = Config()
    config._load_toml_file(str(valid_config_path))

    rule_registry = RuleRegistry(config)
    rule_registry._add_rule(rule_with_config)

    mock_formatter = Mock()
    mock_scorer = Mock()
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
    )
    evaluation.evaluate()

    assert (
        rule_with_config.default_config
        != rule_registry.rules["tests.conftest.rule_with_config"].config
    )
    assert evaluation.results[model1][rule_with_config] is not None
    assert evaluation.results[model2][rule_with_config] is None
