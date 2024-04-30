"""Unit tests for the human readable formatter."""

from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.rule import RuleViolation


def test_human_readable_formatter_model(
    capsys, model1, rule_severity_low, rule_severity_medium, rule_severity_critical
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = HumanReadableFormatter()
    results = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, 10.0)
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """Model \x1B[1mmodel1\x1B[0m
    \x1B[1;32mOK  \x1B[0m tests.conftest.rule_severity_low
    \x1B[1;31mERR \x1B[0m tests.conftest.rule_severity_medium: Oh noes
    \x1B[1;33mWARN\x1B[0m (critical) tests.conftest.rule_severity_critical: Error
Score: \x1B[1m10.0\x1B[0m

"""
    )


def test_human_readable_formatter_project(capsys):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter()
    formatter.project_evaluated(10.0)
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1B[1m10.0\x1B[0m\n"
