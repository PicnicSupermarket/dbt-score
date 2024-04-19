"""Test the CLI."""

import pytest
from click.testing import CliRunner
from dbt_score.cli import lint


def test_invalid_options():
    """Test invalid cli options."""
    runner = CliRunner()
    result = runner.invoke(
        lint, ["--manifest", "fake_manifest.json", "--run-dbt-parse"]
    )
    assert result.exit_code == 2  # pylint: disable=PLR2004


def test_lint_existing_manifest(manifest_path):
    """Test lint with an existing manifest."""
    runner = CliRunner()
    result = runner.invoke(lint, ["--manifest", manifest_path])
    assert result.exit_code == 0


def test_lint_non_existing_manifest():
    """Test lint with a non-existing manifest."""
    runner = CliRunner()

    # Provide manifest in command line
    with pytest.raises(FileNotFoundError):
        runner.invoke(
            lint, ["--manifest", "fake_manifest.json"], catch_exceptions=False
        )

    # Use default manifest path
    with pytest.raises(FileNotFoundError):
        runner.invoke(lint, catch_exceptions=False)
