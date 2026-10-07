"""Test the CLI."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from dbt_score.cli import lint
from dbt_score.dbt_utils import DbtParseException
from dbt_score.scoring import Score


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
    runner = CliRunner()
    # We want to actually test linting the manifest
    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(lint, ["--manifest", manifest_path, "--show", "all"])
        assert result.exit_code == 1  # Expected to fail due to rules in test data


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


def test_lint_unparseable_manifest(tmp_path, caplog):
    """Test lint with a manifest that is not valid JSON."""
    runner = CliRunner()
    invalid_manifest = tmp_path / "manifest.json"
    invalid_manifest.write_text("", encoding="utf-8")

    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(
            lint, ["--manifest", invalid_manifest], catch_exceptions=False
        )

    assert result.exit_code == 2
    assert "dbt's manifest.json could not be parsed" in caplog.text


def passing_evaluation() -> MagicMock:
    """Return a mock evaluation with passing scores."""
    mock_eval = MagicMock()
    mock_eval.project_score = Score(10.0, "🥇")
    mock_eval.scores = {}
    return mock_eval


def test_lint_project_dir(tmp_path, manifest_path):
    """Test lint with a project directory, which is used to find the manifest."""
    runner = CliRunner()
    project_dir = tmp_path / "my_project"
    (project_dir / "target").mkdir(parents=True)
    shutil.copy(manifest_path, project_dir / "target" / "manifest.json")

    with (
        patch("dbt_score.cli.Config._load_toml_file"),
        patch("dbt_score.cli.lint_dbt_project") as mock_lint_dbt_project,
    ):
        mock_lint_dbt_project.return_value = passing_evaluation()
        result = runner.invoke(
            lint, ["--project-dir", str(project_dir)], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert mock_lint_dbt_project.call_args.kwargs["manifest_path"] == (
        project_dir / "target" / "manifest.json"
    )
    assert mock_lint_dbt_project.call_args.kwargs["project_dir"] == project_dir


def test_lint_project_dir_with_manifest(tmp_path, manifest_path):
    """Test lint with a project directory and an explicit manifest."""
    runner = CliRunner()

    with (
        patch("dbt_score.cli.Config._load_toml_file"),
        patch("dbt_score.cli.lint_dbt_project") as mock_lint_dbt_project,
    ):
        mock_lint_dbt_project.return_value = passing_evaluation()
        result = runner.invoke(
            lint,
            ["--project-dir", str(tmp_path), "--manifest", str(manifest_path)],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert mock_lint_dbt_project.call_args.kwargs["manifest_path"] == Path(
        manifest_path
    )
    assert mock_lint_dbt_project.call_args.kwargs["project_dir"] == tmp_path


def test_lint_project_dir_run_dbt_parse(tmp_path):
    """Test lint with a project directory and dbt parse."""
    runner = CliRunner()
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()

    with (
        patch("dbt_score.cli.Config._load_toml_file"),
        patch("dbt_score.cli.dbt_parse") as mock_dbt_parse,
        patch("dbt_score.cli.lint_dbt_project") as mock_lint_dbt_project,
    ):
        mock_lint_dbt_project.return_value = passing_evaluation()
        result = runner.invoke(
            lint,
            ["--project-dir", str(project_dir), "--run-dbt-parse"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    mock_dbt_parse.assert_called_once_with(project_dir=project_dir)


def test_lint_project_dir_non_existing(tmp_path):
    """Test lint with a non-existing project directory."""
    runner = CliRunner()

    with patch("dbt_score.cli.Config._load_toml_file"):
        result = runner.invoke(lint, ["--project-dir", str(tmp_path / "nope")])

    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_lint_dbt_parse_exception(caplog):
    """Test lint with a dbt parse error."""
    runner = CliRunner()

    with patch("dbt_score.cli.dbt_parse") as mock_dbt_parse:
        mock_dbt_parse.side_effect = DbtParseException()
        result = runner.invoke(lint, ["-p"], catch_exceptions=False)
    assert result.exit_code == 2
    assert "dbt parse failed." in caplog.text


def test_lint_dbt_not_installed(caplog, manifest_path):
    """Test lint with a valid manifest when dbt is not installed."""
    runner = CliRunner()

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=False):
        result = runner.invoke(lint, ["-m", manifest_path], catch_exceptions=False)

    # Since our seeds have failing rules that make the exit code 1,
    # we'll accept that as correct behavior
    assert result.exit_code == 1


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
    # Create a mock evaluation with a low project score
    mock_eval = MagicMock()
    mock_eval.project_score = Score(5.0, "🥉")  # Score below 10.0
    mock_eval.scores.values.return_value = []

    with patch("dbt_score.cli.lint_dbt_project") as mock_lint:
        mock_lint.return_value = mock_eval
        runner = CliRunner()
        result = runner.invoke(
            lint, ["--manifest", manifest_path, "--fail-project-under", "10.0"]
        )

        # Since we're mocking the evaluation, we should get exit code 1
        assert result.exit_code == 1


def test_fail_any_item_under(manifest_path):
    """Test `fail_any_item_under`."""
    # Create a mock evaluation with a low model score
    mock_eval = MagicMock()
    mock_eval.project_score = Score(8.0, "🥈")
    # Create a mock scores dict with a low value
    mock_scores = {MagicMock(): Score(4.0, "🥉")}  # Score below 10.0
    mock_eval.scores = mock_scores

    with patch("dbt_score.cli.lint_dbt_project") as mock_lint:
        mock_lint.return_value = mock_eval
        runner = CliRunner()
        result = runner.invoke(
            lint, ["--manifest", manifest_path, "--fail-any-item-under", "10.0"]
        )

        # Since we're mocking the evaluation with a low score, we should get exit code 1
        assert result.exit_code == 1


def test_lint_fail_thresholds_zero(manifest_path):
    """A threshold of 0 is honored (not treated as unset)."""
    mock_eval = MagicMock()
    mock_eval.project_score = Score(0.0, "🚧")
    mock_eval.scores = {MagicMock(): Score(0.0, "🚧")}

    with (
        patch("dbt_score.cli.lint_dbt_project") as mock_lint,
        patch("dbt_score.cli.Config._load_toml_file"),
    ):
        mock_lint.return_value = mock_eval
        runner = CliRunner()
        result = runner.invoke(
            lint,
            [
                "--manifest",
                manifest_path,
                "--fail-project-under",
                "0",
                "--fail-any-item-under",
                "0",
            ],
        )
    # With thresholds at 0 and scores at 0, nothing is strictly under -> pass.
    assert result.exit_code == 0
