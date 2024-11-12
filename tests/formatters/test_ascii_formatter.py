"""Unit tests for the ASCII formatter."""


from dbt_score.evaluation import EvaluableResultsType
from dbt_score.formatters.ascii_formatter import ASCIIFormatter
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


def test_ascii_formatter_model(
    capsys,
    default_config,
    manifest_loader,
    model1,
    rule_severity_low,
    rule_severity_medium,
    rule_severity_critical,
):
    """Ensure the formatter doesn't write anything after model evaluation."""
    formatter = ASCIIFormatter(manifest_loader=manifest_loader, config=default_config)
    results: EvaluableResultsType = {
        rule_severity_low: None,
        rule_severity_medium: Exception("Oh noes"),
        rule_severity_critical: RuleViolation("Error"),
    }
    formatter.evaluable_evaluated(model1, results, Score(10.0, "🥇"))
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_ascii_formatter_project(capsys, default_config, manifest_loader):
    """Ensure the formatter has the correct output after project evaluation."""
    formatter = ASCIIFormatter(manifest_loader=manifest_loader, config=default_config)

    formatter.project_evaluated(Score(10.0, "🥇"))
    stdout_gold = capsys.readouterr().out
    assert len(stdout_gold) > 10

    formatter.project_evaluated(Score(8.0, "🚧"))
    stdout_wip = capsys.readouterr().out
    assert len(stdout_wip) > 10

    assert stdout_gold != stdout_wip
