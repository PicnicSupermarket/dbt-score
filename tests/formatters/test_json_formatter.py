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
    capsys, default_config, manifest_loader, rule_severity_medium
):
    """Ensure evaluables with same name but different types don't overwrite."""
    from dbt_score import Exposure, Model

    # Create evaluables with the same name but different types and unique_ids
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
        name="same_name",  # Same name as model
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

    # Verify they have the same name but different unique_ids
    assert model_same_name.name == exposure_same_name.name == "same_name"
    assert model_same_name.unique_id != exposure_same_name.unique_id

    formatter = JSONFormatter(manifest_loader=manifest_loader, config=default_config)
    results: dict[Type[Rule], RuleViolation | Exception | None] = {
        rule_severity_medium: RuleViolation("Test violation")
    }

    # Evaluate both evaluables with same name
    formatter.evaluable_evaluated(model_same_name, results, Score(5.0, "🥈"))
    formatter.evaluable_evaluated(exposure_same_name, results, Score(7.0, "🥇"))
    formatter.project_evaluated(Score(6.0, "🥈"))

    stdout = capsys.readouterr().out
    output_data = json.loads(stdout)

    # Both evaluables should be present (no collision)
    evaluables = output_data["evaluables"]
    assert len(evaluables) == 2, "Both evaluables with same name should be preserved"

    # Keys should be unique_id, not name
    assert model_same_name.unique_id in evaluables
    assert exposure_same_name.unique_id in evaluables

    # Verify both evaluables maintain their distinct data
    model_data = evaluables[model_same_name.unique_id]
    exposure_data = evaluables[exposure_same_name.unique_id]

    assert model_data["type"] == "model"
    assert model_data["score"] == 5.0
    assert model_data["badge"] == "🥈"

    assert exposure_data["type"] == "exposure"
    assert exposure_data["score"] == 7.0
    assert exposure_data["badge"] == "🥇"
