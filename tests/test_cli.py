"""Test the CLI."""

from unittest.mock import patch

from click.testing import CliRunner
from dbt_score.cli import lint


@patch("dbt_score.cli.dbt_parse")
def test_parse(dbt_parse, manifest_path):
    """Test to ensure dbt parse is not called when the manifest exists."""
    with patch("dbt_score.cli.MANIFEST_PATH", manifest_path):
        runner = CliRunner()
        result1 = runner.invoke(lint)
        result2 = runner.invoke(lint, ["--manifest", manifest_path])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        dbt_parse.assert_not_called()
