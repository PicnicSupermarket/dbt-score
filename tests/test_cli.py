"""Test the CLI."""

from unittest.mock import patch

from click.testing import CliRunner
from dbt_score.cli import lint


def test_invalid_options():
    """Test invalid cli options."""
    runner = CliRunner()
    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(
            lint, ["--manifest", "fake_manifest.json", "--run-dbt-parse"]
        )
        assert result.exit_code == 2  # pylint: disable=PLR2004


def test_lint_existing_manifest(manifest_path):
    """Test lint with an existing manifest."""
    with patch("dbt_score.cli.Config._load_toml_file"):
        runner = CliRunner()
        result = runner.invoke(lint, ["--manifest", manifest_path])

        assert "model1" in result.output
        assert "model2" in result.output
        assert result.exit_code == 0


def test_lint_non_existing_manifest(caplog):
    """Test lint with a non-existing manifest."""
    runner = CliRunner()

    # Provide manifest in command line
    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(
            lint, ["--manifest", "fake_manifest.json"], catch_exceptions=False
        )
        assert result.exit_code == 2
        assert "dbt's manifest.json could not be found" in caplog.text

    # Use default manifest path
    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(lint, catch_exceptions=False)

        assert result.exit_code == 2
        assert "dbt's manifest.json could not be found" in caplog.text
