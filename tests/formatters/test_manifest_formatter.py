"""Unit tests for the manifest formatter."""

import json

from dbt_score.evaluation import EvaluableResultsType
from dbt_score.formatters.manifest_formatter import ManifestFormatter
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


def test_manifest_formatter_model(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = ManifestFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_manifest_formatter_project(
    capsys,
    default_config,
    manifest_loader,
    model1,
    model2,
    source1,
    source2,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = ManifestFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    result1: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    result2: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: None,
        rule_severity_critical: None,
    }

    formatter.evaluable_evaluated(model1, result1, Score(5.0, "🚧"))
    formatter.evaluable_evaluated(model2, result2, Score(10.0, "🥇"))
    formatter.evaluable_evaluated(source1, result1, Score(5.0, "🚧"))
    formatter.evaluable_evaluated(source2, result2, Score(10.0, "🥇"))
    formatter.project_evaluated(Score(7.5, "🥉"))

    stdout = capsys.readouterr().out
    new_manifest = json.loads(stdout)
    assert new_manifest["nodes"]["model.package.model1"]["meta"]["score"] == 5.0
    assert new_manifest["nodes"]["model.package.model1"]["meta"]["badge"] == "🚧"
    assert new_manifest["nodes"]["model.package.model2"]["meta"]["score"] == 10.0
    assert new_manifest["nodes"]["model.package.model2"]["meta"]["badge"] == "🥇"

    assert (
        new_manifest["sources"]["source.package.my_source.table1"]["meta"]["score"]
        == 5.0
    )
    assert (
        new_manifest["sources"]["source.package.my_source.table1"]["meta"]["badge"]
        == "🚧"
    )
    assert (
        new_manifest["sources"]["source.package.my_source.table2"]["meta"]["score"]
        == 10.0
    )
    assert (
        new_manifest["sources"]["source.package.my_source.table2"]["meta"]["badge"]
        == "🥇"
    )
