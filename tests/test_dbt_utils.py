"""Tests for dbt utilities."""

from unittest.mock import MagicMock, patch

import pytest

from dbt_score.dbt_utils import (
    DbtLsException,
    DbtNotInstalledException,
    DbtParseException,
    dbt_ls,
    dbt_parse,
    dbt_required,
    get_default_manifest_path,
)


def test_dbt_parse_exception_str_with_root_cause():
    """The exception message includes the root cause when present."""
    exc = DbtParseException(root_cause=ValueError("boom"))
    assert "dbt parse failed." in str(exc)
    assert "boom" in str(exc)


def test_dbt_parse_exception_str_without_root_cause():
    """The exception message has a fallback when no root cause is set."""
    exc = DbtParseException()
    assert "Root cause not found" in str(exc)


def test_dbt_required_raises_when_not_installed():
    """The decorator raises when dbt is not installed."""

    @dbt_required
    def needs_dbt() -> str:
        return "ok"

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=False):
        with pytest.raises(DbtNotInstalledException):
            needs_dbt()

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True):
        assert needs_dbt() == "ok"


def test_dbt_parse_success():
    """dbt_parse returns the runner result on success."""
    mock_result = MagicMock(success=True)
    mock_runner = MagicMock()
    mock_runner.invoke.return_value = mock_result

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True), patch(
        "dbt_score.dbt_utils.dbtRunner", return_value=mock_runner
    ):
        assert dbt_parse() is mock_result
    mock_runner.invoke.assert_called_once_with(["parse"])


def test_dbt_parse_failure():
    """dbt_parse raises DbtParseException on failure."""
    mock_result = MagicMock(success=False, exception=RuntimeError("nope"))
    mock_runner = MagicMock()
    mock_runner.invoke.return_value = mock_result

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True), patch(
        "dbt_score.dbt_utils.dbtRunner", return_value=mock_runner
    ):
        with pytest.raises(DbtParseException):
            dbt_parse()


def test_dbt_ls_success_with_select_and_exclude():
    """dbt_ls forwards select/exclude and returns the result."""
    mock_result = MagicMock(success=True, result=["model1", "model2"])
    mock_runner = MagicMock()
    mock_runner.invoke.return_value = mock_result

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True), patch(
        "dbt_score.dbt_utils.dbtRunner", return_value=mock_runner
    ):
        result = dbt_ls(select=["model1"], exclude=["model3"])

    assert list(result) == ["model1", "model2"]
    cmd = mock_runner.invoke.call_args.args[0]
    assert "--select" in cmd and "model1" in cmd
    assert "--exclude" in cmd and "model3" in cmd


def test_dbt_ls_without_select_or_exclude():
    """dbt_ls works without select/exclude arguments."""
    mock_result = MagicMock(success=True, result=[])
    mock_runner = MagicMock()
    mock_runner.invoke.return_value = mock_result

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True), patch(
        "dbt_score.dbt_utils.dbtRunner", return_value=mock_runner
    ):
        result = dbt_ls(select=None, exclude=None)

    assert list(result) == []
    cmd = mock_runner.invoke.call_args.args[0]
    assert "--select" not in cmd
    assert "--exclude" not in cmd


def test_dbt_ls_failure():
    """dbt_ls raises DbtLsException on failure."""
    mock_result = MagicMock(success=False, exception=RuntimeError("nope"))
    mock_runner = MagicMock()
    mock_runner.invoke.return_value = mock_result

    with patch("dbt_score.dbt_utils.DBT_INSTALLED", new=True), patch(
        "dbt_score.dbt_utils.dbtRunner", return_value=mock_runner
    ):
        with pytest.raises(DbtLsException):
            dbt_ls(select=None)


def test_get_default_manifest_path(monkeypatch):
    """The default manifest path honors dbt environment variables."""
    monkeypatch.delenv("DBT_PROJECT_DIR", raising=False)
    monkeypatch.delenv("DBT_TARGET_DIR", raising=False)
    assert get_default_manifest_path().name == "manifest.json"
    assert get_default_manifest_path().parent.name == "target"

    monkeypatch.setenv("DBT_TARGET_DIR", "custom_target")
    assert get_default_manifest_path().parent.name == "custom_target"
