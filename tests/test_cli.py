"""Test the CLI."""
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
from dbt_score.cli import lint


@patch("dbt_score.lint.dbt_parse")
def test_parse_not_called(dbt_parse, manifest_path):
    """Test to ensure dbt parse is not called when the manifest exists."""
    runner = CliRunner()
    with patch("dbt_score.cli.get_manifest_path", return_value=manifest_path):
        result1 = runner.invoke(lint)
    result2 = runner.invoke(lint, ["--manifest", manifest_path])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    dbt_parse.assert_not_called()


@patch("dbt_score.lint.dbt_parse")
def test_parse_called(dbt_parse):
    """Test to ensure dbt parse is called when the manifest does not exist."""
    runner = CliRunner()
    with patch(
        "dbt_score.cli.get_manifest_path", return_value=Path("fake_manifest.json")
    ):
        runner.invoke(lint)

    dbt_parse.assert_called_once()
