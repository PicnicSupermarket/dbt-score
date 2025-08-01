"""Unit tests for the JSON formatter."""

import json
from typing import Type

from dbt_score.formatters.json_formatter import JSONFormatter
from dbt_score.rule import Rule, RuleViolation
from dbt_score.scoring import Score


def test_json_formatter(
    capsys,
    default_config,
    manifest_loader,
    model1,
    source1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after evaluation."""
    formatter = JSONFormatter(manifest_loader=manifest_loader, config=default_config)
    results: dict[Type[Rule], RuleViolation | Exception | None] = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    formatter.evaluable_evaluated(source1, results, Score(10.0, "🥇"))
    formatter.project_evaluated(Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """{
  "evaluables": {
    "model.package.model1": {
      "score": 10.0,
      "badge": "🥇",
      "pass": true,
      "results": {
        "tests.conftest.rule_severity_low": {
          "result": "OK",
          "severity": "low",
          "message": null
        },
        "tests.conftest.rule_severity_medium": {
          "result": "ERR",
          "severity": "medium",
          "message": "Oh noes"
        },
        "tests.conftest.rule_severity_critical": {
          "result": "WARN",
          "severity": "critical",
          "message": "Error"
        }
      },
      "type": "model"
    },
    "source.package.my_source.table1": {
      "score": 10.0,
      "badge": "🥇",
      "pass": true,
      "results": {
        "tests.conftest.rule_severity_low": {
          "result": "OK",
          "severity": "low",
          "message": null
        },
        "tests.conftest.rule_severity_medium": {
          "result": "ERR",
          "severity": "medium",
          "message": "Oh noes"
        },
        "tests.conftest.rule_severity_critical": {
          "result": "WARN",
          "severity": "critical",
          "message": "Error"
        }
      },
      "type": "source"
    }
  },
  "project": {
    "score": 10.0,
    "badge": "🥇",
    "pass": true
  }
}
"""
    )


def test_json_formatter_name_collision_prevention(
    capsys,
    default_config,
    manifest_loader,
):
    """Ensure the formatter handles evaluables with same name but different types."""
    from dbt_score import Exposure, Model, Severity, rule

    @rule(severity=Severity.MEDIUM)
    def test_rule(model: Model) -> RuleViolation | None:
        """Test rule for models."""
        return RuleViolation("Test violation")

    # Create mock evaluables with the same name but different types
    model_same_name = Model(
        unique_id="model.package.same_name",
        name="same_name",
        relation_name="db.schema.same_name",
        description="A model",
        original_file_path="models/same_name.sql",
        config={},
        meta={},
        columns=[],
        package_name="package",
        database="db",
        schema="schema",
        raw_code="SELECT 1",
        language="sql",
        access="public",
        group="default",
        alias=None,
        patch_path=None,
        tags=[],
        tests=[],
        depends_on={},
        parents=[],
        children=[],
        _raw_values={},
        _raw_test_values=[],
    )

    exposure_same_name = Exposure(
        unique_id="exposure.package.same_name",
        name="same_name",
        description="An exposure",
        label="Same Name Exposure",
        url="https://example.com",
        maturity="medium",
        original_file_path="models/exposures.yml",
        type="dashboard",
        owner={"name": "test", "email": "test@example.com"},
        config={},
        meta={},
        tags=[],
        depends_on={},
        parents=[],
        _raw_values={},
    )

    formatter = JSONFormatter(manifest_loader=manifest_loader, config=default_config)
    results: dict[Type[Rule], RuleViolation | Exception | None] = {
        test_rule: RuleViolation("Test violation")
    }

    # Evaluate both evaluables
    formatter.evaluable_evaluated(model_same_name, results, Score(5.0, "🥈"))
    formatter.evaluable_evaluated(exposure_same_name, results, Score(7.0, "🥇"))
    formatter.project_evaluated(Score(6.0, "🥈"))

    stdout = capsys.readouterr().out
    output_data = json.loads(stdout)

    # Verify both evaluables are present with unique keys
    evaluables = output_data["evaluables"]
    assert len(evaluables) == 2, "Both evaluables should be present"

    assert "model.package.same_name" in evaluables, "Model should use unique_id as key"
    assert (
        "exposure.package.same_name" in evaluables
    ), "Exposure should use unique_id as key"

    # Verify the data integrity
    model_data = evaluables["model.package.same_name"]
    exposure_data = evaluables["exposure.package.same_name"]

    assert model_data["type"] == "model"
    assert model_data["score"] == 5.0
    assert model_data["badge"] == "🥈"

    assert exposure_data["type"] == "exposure"
    assert exposure_data["score"] == 7.0
    assert exposure_data["badge"] == "🥇"
