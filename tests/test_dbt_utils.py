"""Unit tests for the dbt utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dbt_score.dbt_utils import (
    DbtLsException,
    DbtParseException,
    dbt_ls,
    dbt_parse,
    get_default_manifest_path,
)


def test_get_default_manifest_path(monkeypatch, tmp_path):
    """Test the default manifest path, relative to the current working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DBT_PROJECT_DIR", raising=False)
    monkeypatch.delenv("DBT_TARGET_DIR", raising=False)

    assert get_default_manifest_path() == tmp_path / "target" / "manifest.json"


def test_get_default_manifest_path_env(monkeypatch, tmp_path):
    """Test the default manifest path, using dbt's environment variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DBT_PROJECT_DIR", "my_project")
    monkeypatch.setenv("DBT_TARGET_DIR", "my_target")

    assert get_default_manifest_path() == (
        tmp_path / "my_project" / "my_target" / "manifest.json"
    )


def test_get_default_manifest_path_project_dir(monkeypatch, tmp_path):
    """Test the default manifest path, using an explicit project directory."""
    monkeypatch.setenv("DBT_PROJECT_DIR", "ignored")
    monkeypatch.delenv("DBT_TARGET_DIR", raising=False)

    assert get_default_manifest_path(tmp_path / "my_project") == (
        tmp_path / "my_project" / "target" / "manifest.json"
    )


@pytest.mark.parametrize(
    "project_dir,expected_cmd",
    [
        (None, ["parse"]),
        (Path("my_project"), ["parse", "--project-dir", "my_project"]),
    ],
)
def test_dbt_parse(project_dir, expected_cmd):
    """Test that dbt parse is invoked with the project directory."""
    with patch("dbt_score.dbt_utils.dbtRunner") as mock_runner:
        mock_runner.return_value.invoke.return_value = MagicMock(success=True)
        dbt_parse(project_dir=project_dir)

    mock_runner.return_value.invoke.assert_called_once_with(expected_cmd)


def test_dbt_parse_failure():
    """Test that a failing dbt parse raises an exception."""
    with patch("dbt_score.dbt_utils.dbtRunner") as mock_runner:
        mock_runner.return_value.invoke.return_value = MagicMock(
            success=False, exception=RuntimeError("boom")
        )
        with pytest.raises(DbtParseException, match="boom"):
            dbt_parse()


def test_dbt_ls_project_dir():
    """Test that dbt ls is invoked with the project directory."""
    with patch("dbt_score.dbt_utils.dbtRunner") as mock_runner:
        mock_runner.return_value.invoke.return_value = MagicMock(
            success=True, result=["model1"]
        )
        result = dbt_ls(["+model1"], ["model2"], project_dir=Path("my_project"))

    assert result == ["model1"]
    cmd = mock_runner.return_value.invoke.call_args.args[0]
    assert cmd[:2] == ["ls", "--resource-types"]
    assert cmd[-6:] == [
        "--select",
        "+model1",
        "--exclude",
        "model2",
        "--project-dir",
        "my_project",
    ]


def test_dbt_ls_failure():
    """Test that a failing dbt ls raises an exception."""
    with patch("dbt_score.dbt_utils.dbtRunner") as mock_runner:
        mock_runner.return_value.invoke.return_value = MagicMock(
            success=False, exception=RuntimeError("boom")
        )
        with pytest.raises(DbtLsException):
            dbt_ls(["+model1"])
