"""Test the CLI."""

from unittest.mock import patch

from click.testing import CliRunner
from dbt_score.cli import lint
from dbt_score.dbt_utils import DbtParseException


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


def test_lint_dbt_parse_exception(caplog):
    """Test lint with a dbt parse error."""
    runner = CliRunner()

    with patch("dbt_score.cli.dbt_parse") as mock_dbt_parse:
        mock_dbt_parse.side_effect = DbtParseException("parsing error")
        result = runner.invoke(lint, ["-p"], catch_exceptions=False)
    assert result.exit_code == 2
    assert "dbt failed to parse project" in caplog.text


def test_lint_dbt_not_installed(caplog, manifest_path):
    """Test lint with a valid manifest when dbt is not installed."""
    runner = CliRunner()

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=False):
        result = runner.invoke(lint, ["-m", manifest_path], catch_exceptions=False)
    assert result.exit_code == 0


def test_lint_dbt_not_installed_v(caplog):
    """Test lint with dbt parse when dbt is not installed."""
    runner = CliRunner()

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=False):
        result = runner.invoke(lint, ["-p"])
    assert result.exit_code == 2
    assert "DbtNotInstalledException" in caplog.text


def test_lint_other_exception(manifest_path, caplog):
    """Test lint with an unexpected error."""
    runner = CliRunner()

    with patch("dbt_score.cli.lint_dbt_project") as mock_lint_dbt_project:
        mock_lint_dbt_project.side_effect = Exception("some error")
        result = runner.invoke(
            lint, ["--manifest", manifest_path], catch_exceptions=False
        )
    assert result.exit_code == 2
    assert caplog.text.startswith("ERROR")


def test_fail_project_under(manifest_path):
    """Test `fail_project_under`."""
    with patch("dbt_score.cli.Config._load_toml_file"):
        runner = CliRunner()
        result = runner.invoke(
            lint, ["--manifest", manifest_path, "--fail_project_under", "10.0"]
        )

        assert "model1" in result.output
        assert "model2" in result.output
        assert "Error: project score too low, fail_project_under" in result.stdout
        assert result.exit_code == 1


def test_fail_any_model_under(manifest_path):
    """Test `fail_any_model_under`."""
    with patch("dbt_score.cli.Config._load_toml_file"):
        runner = CliRunner()
        result = runner.invoke(
            lint, ["--manifest", manifest_path, "--fail_any_model_under", "10.0"]
        )

        assert "model1" in result.output
        assert "model2" in result.output
        assert "Error: model score too low, fail_any_model_under" in result.stdout
        assert result.exit_code == 1
