"""Unit tests for the human readable formatter."""

from textwrap import dedent

import pytest
from dbt_score.evaluation import EvaluableResultsType
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


def test_human_readable_formatter_model_with_defaults(
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
    results: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    expected = """\
    🥇 \x1b[1mModel: model1\x1b[0m (score: 10.0)
        \x1b[1;31mERR \x1b[0m tests.conftest.rule_severity_medium: Oh noes
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    """
    assert stdout == dedent(expected)


@pytest.mark.parametrize(
    "show,expected",
    [
        (
            "all",
            """\
    🥇 \x1b[1mModel: model1\x1b[0m (score: 10.0)
        \x1b[1;32mOK  \x1b[0m tests.conftest.rule_severity_low
        \x1b[1;31mERR \x1b[0m tests.conftest.rule_severity_medium: Oh noes
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    """,
        ),
        (
            "failing-rules",
            """\
    🥇 \x1b[1mModel: model1\x1b[0m (score: 10.0)
        \x1b[1;31mERR \x1b[0m tests.conftest.rule_severity_medium: Oh noes
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    """,
        ),
        (
            "failing-items",
            "",
        ),
    ],
)
def test_human_readable_formatter_model_show_parameter(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
    show,
    expected,
):
    """Ensure the formatter has the correct output after model evaluation."""
    default_config.overload({"show": show})
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == dedent(expected)


def test_human_readable_formatter_project(capsys, default_config, manifest_loader):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    formatter.project_evaluated(Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1b[1m10.0\x1b[0m 🥇\n"


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
    default_config.overload({"show": "all"})
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(9.99, "🥈"))
    stdout = capsys.readouterr().out

    expected = """\
    🥈 \x1b[1mModel: model1\x1b[0m (score: 9.9)
        \x1b[1;32mOK  \x1b[0m tests.conftest.rule_severity_low
        \x1b[1;31mERR \x1b[0m tests.conftest.rule_severity_medium: Oh noes
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    """
    assert stdout == dedent(expected)


def test_human_readable_formatter_near_perfect_project_score(
    capsys, default_config, manifest_loader
):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    formatter.project_evaluated(Score(9.99, "🥈"))
    stdout = capsys.readouterr().out
    assert stdout == "Project score: \x1b[1m9.9\x1b[0m 🥈\n"


def test_human_readable_formatter_low_evaluable_score(
    capsys,
    default_config,
    manifest_loader,
    model1,
    source1,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output when a model has a low score."""
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: EvaluableResultsType = {
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(0.0, "🚧"))
    formatter.evaluable_evaluated(source1, results, Score(0.0, "🚧"))
    formatter.project_evaluated(Score(0.0, "🚧"))
    stdout = capsys.readouterr().out

    expected = """\
    🚧 \x1b[1mModel: model1\x1b[0m (score: 0.0)
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    🚧 \x1b[1mSource: my_source.table1\x1b[0m (score: 0.0)
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    Project score: \x1b[1m0.0\x1b[0m 🚧

    Error: evaluable score too low, fail_any_item_under = 5.0
    Model model1 scored 0.0
    Source my_source.table1 scored 0.0
    """
    assert stdout == dedent(expected)


def test_human_readable_formatter_low_project_score_high_model_score(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_critical,
):
    """Ensure the formatter has the correct output when the projet has a low score.

    If model itself has a high project score then we need to pass `show_all` flag
    to make it visible.
    """
    default_config.overload({"show_all": True})
    formatter = HumanReadableFormatter(
        manifest_loader=manifest_loader, config=default_config
    )
    results: EvaluableResultsType = {
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    formatter.project_evaluated(Score(0.0, "🚧"))
    stdout = capsys.readouterr().out

    expected = """\
    🥇 \x1b[1mModel: model1\x1b[0m (score: 10.0)
        \x1b[1;33mWARN\x1b[0m (critical) tests.conftest.rule_severity_critical: Error

    Project score: \x1b[1m0.0\x1b[0m 🚧

    Error: project score too low, fail_project_under = 5.0
    """
    assert stdout == dedent(expected)
