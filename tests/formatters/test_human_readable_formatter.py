"""Unit tests for the human readable formatter."""

from typing import Type

from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.rule import Rule, RuleViolation
from dbt_score.scoring import Score


def test_human_readable_formatter_model(
    capsys,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = HumanReadableFormatter(manifest_loader=manifest_loader)
    results: dict[Type[Rule], RuleViolation | Exception | None] = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """🥇 \x1B[1mmodel1\x1B[0m (score: 10.0)
    \x1B[1;32mOK  \x1B[0m tests.conftest.rule_severity_low
    \x1B[1;31mERR \x1B[0m tests.conftest.rule_severity_medium: Oh noes
    \x1B[1;33mWARN\x1B[0m (critical) tests.conftest.rule_severity_critical: Error

"""
    )


def test_human_readable_formatter_project(capsys, manifest_loader):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter(manifest_loader=manifest_loader)
    formatter.project_evaluated(Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1B[1m10.0\x1B[0m 🥇\n"
