"""Test models."""

from pathlib import Path
from unittest.mock import patch

from dbt_score.models import ManifestLoader


@patch("dbt_score.models.Path.read_text")
def test_manifest_load(mock_read_text, raw_manifest):
    """Test loading a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        loader = ManifestLoader(Path("some.json"))
        assert len(loader.models) == len(
            [
                node
                for node in raw_manifest["nodes"].values()
                if node["resource_type"] == "model"
            ]
        )
        assert loader.models[0].tests[0].name == "test2"
        assert loader.models[0].columns[0].tests[0].name == "test1"


@patch("dbt_score.models.Path.read_text")
def test_manifest_select_models_simple(mock_read_text, raw_manifest):
    """Test selecting a simple selection in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"))

    assert [x.name for x in manifest_loader.models] == ["model1", "model2"]

    manifest_loader.select_models(["model1"])
    assert [x.name for x in manifest_loader.models] == ["model1"]


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_models_dbt_ls(mock_dbt_ls, mock_read_text, raw_manifest):
    """Test selecting a complex selection in a manifest, which uses dbt ls."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"))

    assert [x.name for x in manifest_loader.models] == ["model1", "model2"]

    mock_dbt_ls.return_value = ["model1"]
    manifest_loader.select_models(["+model1"])
    assert [x.name for x in manifest_loader.models] == ["model1"]
    mock_dbt_ls.assert_called_once_with(["+model1"])
