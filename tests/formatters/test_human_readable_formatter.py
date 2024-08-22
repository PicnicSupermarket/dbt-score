"""Unit tests for the human readable formatter."""

from dbt_score.evaluation import ModelResultsType
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


def test_human_readable_formatter_model(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: ModelResultsType = {
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


def test_human_readable_formatter_project(capsys, default_config, manifest_loader):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    formatter.project_evaluated(Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1B[1m10.0\x1B[0m 🥇\n"


def test_human_readable_formatter_near_perfect_model_score(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output after model evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: ModelResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, Score(9.99, "🥈"))
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """🥈 \x1B[1mmodel1\x1B[0m (score: 9.9)
    \x1B[1;32mOK  \x1B[0m tests.conftest.rule_severity_low
    \x1B[1;31mERR \x1B[0m tests.conftest.rule_severity_medium: Oh noes
    \x1B[1;33mWARN\x1B[0m (critical) tests.conftest.rule_severity_critical: Error

"""
    )


def test_human_readable_formatter_near_perfect_project_score(
    capsys, default_config, manifest_loader
):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    formatter.project_evaluated(Score(9.99, "🥈"))
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1B[1m9.9\x1B[0m 🥈\n"


def test_human_readable_formatter_low_model_score(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output when a model has a low score."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: ModelResultsType = {
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, Score(0.0, "🚧"))
    formatter.project_evaluated(Score(0.0, "🚧"))
    stdout = capsys.readouterr().out
    print()
    assert (
        stdout
        == """🚧 \x1B[1mmodel1\x1B[0m (score: 0.0)
    \x1B[1;33mWARN\x1B[0m (critical) tests.conftest.rule_severity_critical: Error

Project score: \x1B[1m0.0\x1B[0m 🚧

Error: model score too low, fail_any_model_under = 5.0
Model model1 scored 0.0
"""
    )


def test_human_readable_formatter_low_project_score(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output when the projet has a low score."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: ModelResultsType = {
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.model_evaluated(model1, results, Score(10.0, "🥇"))
    formatter.project_evaluated(Score(0.0, "🚧"))
    stdout = capsys.readouterr().out
    print()
    assert (
        stdout
        == """🥇 \x1B[1mmodel1\x1B[0m (score: 10.0)
    \x1B[1;33mWARN\x1B[0m (critical) tests.conftest.rule_severity_critical: Error

Project score: \x1B[1m0.0\x1B[0m 🚧

Error: project score too low, fail_project_under = 5.0
"""
    )
