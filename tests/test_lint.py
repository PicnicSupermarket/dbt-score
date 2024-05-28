"""Unit tests for the linting functionality."""


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
def test_lint_dbt_project_with_select(
    mock_manifest_loader, mock_evaluation, manifest_path
):
    """Test linting the dbt project with --select model1."""
    # Instance of classes are the same Mocks
    mock_evaluation.return_value = mock_evaluation
    mock_manifest_loader.return_value = mock_manifest_loader

    lint_dbt_project(
        manifest_path=manifest_path, config=Config(), format="plain", select=["model1"]
    )

    mock_evaluation.evaluate.assert_called_once()
    mock_manifest_loader.select_models.assert_called_once_with(["model1"])
