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
        config=default_config,
    )
    evaluation.evaluate()

    model1 = manifest_loader.models["model.package.model1"]
    model2 = manifest_loader.models["model.package.model2"]

    assert evaluation.results[model1][rule_severity_low] is None
    assert evaluation.results[model1][rule_severity_medium] is None
    assert evaluation.results[model1][rule_severity_high] is None
    assert isinstance(evaluation.results[model1][rule_error], Exception)

    assert isinstance(evaluation.results[model2][rule_severity_low], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_medium], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_severity_high], RuleViolation)
    assert isinstance(evaluation.results[model2][rule_error], Exception)

    # Calculate total number of evaluables
    total_evaluables = (
        len(manifest_loader.models)
        + len(manifest_loader.sources)
        + len(manifest_loader.snapshots)
        + len(manifest_loader.seeds)
        + len(manifest_loader.exposures)
    )
    assert mock_formatter.evaluable_evaluated.call_count == total_evaluables
    assert mock_formatter.project_evaluated.call_count == 1

    assert mock_scorer.score_evaluable.call_count == total_evaluables
    assert mock_scorer.score_aggregate_evaluables.call_count == 1


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
        config=default_config,
    )

    evaluation.evaluate()

    # Access model directly by its key
    model2 = manifest_loader.models["model.package.model2"]
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
        config=default_config,
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
        config=default_config,
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
        config=default_config,
    )
    evaluation.evaluate()

    assert len(evaluation.results) == 0
    assert list(evaluation.scores.values()) == []


def test_evaluation_rule_with_config(
    manifest_path, rule_with_config, valid_config_path, default_config
):
    """Test rule evaluation with parameters."""
    manifest_loader = ManifestLoader(manifest_path)

    model1 = manifest_loader.models["model.package.model1"]
    model2 = manifest_loader.models["model.package.model2"]

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
        config=default_config,
    )
    evaluation.evaluate()

    assert (
        rule_with_config.default_config
        != rule_registry.rules["tests.conftest.rule_with_config"].config
    )
    assert evaluation.results[model1][rule_with_config] is not None
    assert evaluation.results[model2][rule_with_config] is None


def test_evaluation_with_filter(
    manifest_path,
    default_config,
    model_rule_with_filter,
    source_rule_with_filter,
    snapshot_rule_with_filter,
    exposure_rule_with_filter,
):
    """Test rule with filter."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()
    mock_scorer = Mock()

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(model_rule_with_filter)
    rule_registry._add_rule(source_rule_with_filter)
    rule_registry._add_rule(snapshot_rule_with_filter)
    rule_registry._add_rule(exposure_rule_with_filter)
    # Ensure we get a valid Score object from the Mock
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
        config=default_config,
    )
    evaluation.evaluate()

    model1 = manifest_loader.models["model.package.model1"]
    model2 = manifest_loader.models["model.package.model2"]
    source1 = manifest_loader.sources["source.package.my_source.table1"]
    source2 = manifest_loader.sources["source.package.my_source.table2"]
    snapshot1 = manifest_loader.snapshots["snapshot.package.snapshot1"]
    snapshot2 = manifest_loader.snapshots["snapshot.package.snapshot2"]
    exposure1 = manifest_loader.exposures["exposure.package.exposure1"]
    exposure2 = manifest_loader.exposures["exposure.package.exposure2"]

    assert model_rule_with_filter not in evaluation.results[model1]
    assert isinstance(evaluation.results[model2][model_rule_with_filter], RuleViolation)

    assert source_rule_with_filter not in evaluation.results[source1]
    assert isinstance(
        evaluation.results[source2][source_rule_with_filter], RuleViolation
    )

    assert snapshot_rule_with_filter not in evaluation.results[snapshot1]
    assert isinstance(
        evaluation.results[snapshot2][snapshot_rule_with_filter], RuleViolation
    )

    assert exposure_rule_with_filter not in evaluation.results[exposure1]
    assert isinstance(
        evaluation.results[exposure2][exposure_rule_with_filter], RuleViolation
    )


def test_evaluation_with_class_filter(
    manifest_path,
    default_config,
    model_class_rule_with_filter,
    source_class_rule_with_filter,
    snapshot_class_rule_with_filter,
    exposure_class_rule_with_filter,
):
    """Test rule with filters and filtered rules defined by classes."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()
    mock_scorer = Mock()

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(model_class_rule_with_filter)
    rule_registry._add_rule(source_class_rule_with_filter)
    rule_registry._add_rule(snapshot_class_rule_with_filter)
    rule_registry._add_rule(exposure_class_rule_with_filter)
    # Ensure we get a valid Score object from the Mock
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
        config=default_config,
    )
    evaluation.evaluate()

    # Access entities directly by their keys
    model1 = manifest_loader.models["model.package.model1"]
    model2 = manifest_loader.models["model.package.model2"]
    source1 = manifest_loader.sources["source.package.my_source.table1"]
    source2 = manifest_loader.sources["source.package.my_source.table2"]
    snapshot1 = manifest_loader.snapshots["snapshot.package.snapshot1"]
    snapshot2 = manifest_loader.snapshots["snapshot.package.snapshot2"]
    exposure1 = manifest_loader.exposures["exposure.package.exposure1"]
    exposure2 = manifest_loader.exposures["exposure.package.exposure2"]

    assert model_class_rule_with_filter not in evaluation.results[model1]
    assert isinstance(
        evaluation.results[model2][model_class_rule_with_filter], RuleViolation
    )

    assert source_class_rule_with_filter not in evaluation.results[source1]
    assert isinstance(
        evaluation.results[source2][source_class_rule_with_filter], RuleViolation
    )

    assert snapshot_class_rule_with_filter not in evaluation.results[snapshot1]
    assert isinstance(
        evaluation.results[snapshot2][snapshot_class_rule_with_filter], RuleViolation
    )

    assert exposure_class_rule_with_filter not in evaluation.results[exposure1]
    assert isinstance(
        evaluation.results[exposure2][exposure_class_rule_with_filter], RuleViolation
    )


def test_evaluation_with_models_and_sources(
    manifest_path,
    default_config,
    decorator_rule,
    decorator_rule_source,
    decorator_rule_snapshot,
    decorator_rule_exposure,
):
    """Test that model rules apply to models and vice versa."""
    manifest_loader = ManifestLoader(manifest_path)
    mock_formatter = Mock()
    mock_scorer = Mock()

    rule_registry = RuleRegistry(default_config)
    rule_registry._add_rule(decorator_rule)
    rule_registry._add_rule(decorator_rule_source)
    rule_registry._add_rule(decorator_rule_snapshot)
    rule_registry._add_rule(decorator_rule_exposure)

    # Ensure we get a valid Score object from the Mock
    mock_scorer.score_model.return_value = Score(10, "🥇")

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=mock_formatter,
        scorer=mock_scorer,
        config=default_config,
    )
    evaluation.evaluate()

    model1 = manifest_loader.models["model.package.model1"]
    source1 = manifest_loader.sources["source.package.my_source.table1"]
    snapshot1 = manifest_loader.snapshots["snapshot.package.snapshot1"]
    exposure1 = manifest_loader.exposures["exposure.package.exposure1"]

    assert decorator_rule in evaluation.results[model1]
    assert decorator_rule_source not in evaluation.results[model1]
    assert decorator_rule_snapshot not in evaluation.results[model1]
    assert decorator_rule_exposure not in evaluation.results[model1]

    assert decorator_rule_source in evaluation.results[source1]
    assert decorator_rule not in evaluation.results[source1]
    assert decorator_rule_snapshot not in evaluation.results[source1]
    assert decorator_rule_exposure not in evaluation.results[source1]

    assert decorator_rule_snapshot in evaluation.results[snapshot1]
    assert decorator_rule_source not in evaluation.results[snapshot1]
    assert decorator_rule not in evaluation.results[snapshot1]
    assert decorator_rule_exposure not in evaluation.results[snapshot1]

    assert decorator_rule_exposure in evaluation.results[exposure1]
    assert decorator_rule not in evaluation.results[exposure1]
    assert decorator_rule_source not in evaluation.results[exposure1]
    assert decorator_rule_snapshot not in evaluation.results[exposure1]
