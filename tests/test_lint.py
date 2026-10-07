"""Unit tests for the linting functionality."""

from pathlib import Path
from unittest.mock import patch

from dbt_score.config import Config
from dbt_score.lint import lint_dbt_project


@patch("dbt_score.lint.Evaluation")
def test_lint_dbt_project(mock_evaluation, manifest_path):
    """Test linting the dbt project."""
    # Instance of classes are the same Mocks
    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(manifest_path=manifest_path, config=Config(), format="plain")

    mock_evaluation.evaluate.assert_called_once()


@patch("dbt_score.lint.Evaluation")
@patch("dbt_score.lint.ManifestLoader")
def test_lint_dbt_project_project_dir(
    mock_manifest_loader, mock_evaluation, manifest_path
):
    """Test that the project directory is passed on to the manifest loader."""
    lint_dbt_project(
        manifest_path=manifest_path,
        config=Config(),
        format="plain",
        select=["+model1"],
        project_dir=Path("my_project"),
    )

    mock_manifest_loader.assert_called_once_with(
        manifest_path,
        select=["+model1"],
        exclude=None,
        project_dir=Path("my_project"),
    )


@patch("dbt_score.lint.Evaluation")
@patch("dbt_score.lint.ManifestLoader")
@patch("dbt_score.lint.RuleRegistry.load_all")
def test_lint_dbt_project_loads_rules_from_project_dir(
    mock_load_all, mock_manifest_loader, mock_evaluation, manifest_path
):
    """Test that local rules are loaded from the project directory."""
    lint_dbt_project(
        manifest_path=manifest_path,
        config=Config(),
        format="plain",
        project_dir=Path("my_project"),
    )

    mock_load_all.assert_called_once_with(project_dir=Path("my_project"))
