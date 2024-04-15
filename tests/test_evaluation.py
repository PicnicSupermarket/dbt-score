"""Unit tests for the evaluation module."""

from unittest.mock import Mock

from dbt_score.evaluation import Evaluation
from dbt_score.models import ManifestLoader
from dbt_score.rule import RuleViolation
from dbt_score.rule_registry import RuleRegistry


def test_evaluation_low_medium_high(
    manifest_path,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_high,
    rule_error,
):
    """Test rule evaluation with a combination of LOW, MEDIUM and HIGH severity."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()

    rule_registry = RuleRegistry()
    rule_registry._add_rule("rule_severity_low", rule_severity_low)
    rule_registry._add_rule("rule_severity_medium", rule_severity_medium)
    rule_registry._add_rule("rule_severity_high", rule_severity_high)
    rule_registry._add_rule("rule_error", rule_error)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
    )
    evaluation.evaluate()

    model1 = manifest_loader.models[0]
    model2 = manifest_loader.models[1]

    assert evaluation.results[model1][rule_severity_low] is None
    assert evaluation.results[model1][rule_severity_medium] is None
    assert evaluation.results[model1][rule_severity_high] is None
    assert isinstance(evaluation.results[model1][rule_error], Exception)
    assert evaluation.scores[model1] == 1.0

    assert isinstance(evaluation.results[model2][rule_severity_low], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_medium], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_high], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_error], Exception)
    assert evaluation.scores[model2] == 0.5

    assert evaluation.project_score == 0.75

    assert mock_formatter.model_evaluated.call_count == 2
    assert mock_formatter.project_evaluated.call_count == 1


def test_evaluation_critical(
    manifest_path,
    rule_severity_low,
    rule_severity_critical,
):
    """Test rule evaluation with a CRITICAL severity."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()

    rule_registry = RuleRegistry()
    rule_registry._add_rule("rule_severity_low", rule_severity_low)
    rule_registry._add_rule("rule_severity_critical", rule_severity_critical)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
    )
    evaluation.evaluate()

    model2 = manifest_loader.models[1]

    assert isinstance(evaluation.results[model2][rule_severity_critical], RuleViolation)
    assert evaluation.scores[model2] == 0.0

    assert evaluation.project_score == 0.5


def test_evaluation_no_rule(manifest_path):
    """Test rule evaluation when no rule exists."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()

    rule_registry = RuleRegistry()

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
    )
    evaluation.evaluate()

    assert list(evaluation.scores.values()) == [1.0, 1.0]
    assert evaluation.project_score == 1.0


def test_evaluation_no_model(manifest_empty_path, rule_severity_low):
    """Test rule evaluation when no model exists."""
    manifest_loader = ManifestLoader(manifest_empty_path)
    mock_formatter = Mock()

    rule_registry = RuleRegistry()
    rule_registry._add_rule("rule_severity_low", rule_severity_low)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
    )
    evaluation.evaluate()

    assert list(evaluation.scores.values()) == []
    assert evaluation.project_score == 1.0


def test_evaluation_no_model_no_rule(manifest_empty_path):
    """Test rule evaluation when no rule and no model exists."""
    manifest_loader = ManifestLoader(manifest_empty_path)
    mock_formatter = Mock()

    rule_registry = RuleRegistry()

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
    )
    evaluation.evaluate()

    assert list(evaluation.scores.values()) == []
    assert evaluation.project_score == 1.0