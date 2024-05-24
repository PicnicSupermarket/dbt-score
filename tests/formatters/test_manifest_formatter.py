"""Unit tests for the manifest formatter."""

import json
from typing import Type

from dbt_score.formatters.manifest_formatter import ManifestFormatter
from dbt_score.rule import Rule, RuleViolation


def test_manifest_formatter_model(
    capsys,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = ManifestFormatter(manifest_loader=manifest_loader)
    results = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, 10.0)
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_human_readable_formatter_project(  # noqa: PLR0913
    capsys,
    manifest_loader,
    model1,
    model2,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = ManifestFormatter(manifest_loader=manifest_loader)
    result1: dict[Type[Rule], RuleViolation | Exception | None] = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    result2: dict[Type[Rule], RuleViolation | Exception | None] = {
        rule_severity_low: None,
        rule_severity_medium: None,
        rule_severity_critical: None,
    }

    formatter.model_evaluated(model1, result1, 5.0)
    formatter.model_evaluated(model2, result2, 10.0)
    formatter.project_evaluated(7.5)
    stdout = capsys.readouterr().out
    new_manifest = json.loads(stdout)
    assert new_manifest["nodes"]["model.package.model1"]["meta"]["score"] == 5.0
    assert new_manifest["nodes"]["model.package.model2"]["meta"]["score"] == 10.0
