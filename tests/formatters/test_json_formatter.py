"""Unit tests for the JSON formatter."""

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
    "model1": {
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
    "table1": {
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
